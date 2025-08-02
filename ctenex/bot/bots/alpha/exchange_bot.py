import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

import httpx
from loguru import logger
from sqlalchemy import text

from ctenex.bot.db.async_session import AsyncSessionStream, db
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderAddResponse,
    OrderGetResponse,
)
from ctenex.utils.contracts import validate_contract_id


class ExchangeBot:
    def __init__(
        self,
        trader_id: UUID,
        contract_id: str,
        base_url: str,
        number_of_orders: int = 2,
        sample_interval: Decimal = Decimal(1000.0),  # ms
        poll_interval: Decimal = Decimal(1000.0),  # ms
    ):
        # Configuration
        self.base_url = base_url
        self.trader_id = trader_id
        self.contract_id = contract_id
        self.sample_interval = sample_interval
        self.poll_interval = poll_interval
        self.number_of_orders = number_of_orders
        self.last_processed_order_timestamp: datetime = datetime.now(timezone.utc)

        # Dependencies
        self.exchange_client = httpx.AsyncClient(base_url=base_url)

    async def validate_contract_id(self) -> None:
        contract = validate_contract_id(self.contract_id, self.base_url)
        self.tick_size = contract.tick_size

    async def get_orders(
        self,
        contract_id: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[OrderGetResponse]:
        # TODO: Validate both start_time and end_time are provided
        logger.debug(f"Getting orders for contract {contract_id}")

        query_parameters = {
            "contract_id": contract_id,
            "sort_by": "placed_at",
            "sort_order": "asc",
        }
        if start_time:
            query_parameters["placed_at_or_after"] = str(start_time)
        if end_time:
            query_parameters["placed_before"] = str(end_time)

        response = await self.exchange_client.get(
            url="/v1/stateless/orders",
            params=query_parameters,
        )
        response.raise_for_status()
        return [OrderGetResponse(**order) for order in response.json()]

    async def place_order(self, order: OrderAddRequest) -> OrderAddResponse:
        response = await self.exchange_client.post(
            url="/v1/stateless/orders", json=order.model_dump(mode="json")
        )
        response.raise_for_status()
        logger.info(f"Placed order: {response.json()}")
        return OrderAddResponse(**response.json())

    async def process_orders(
        self,
        orders: list[OrderGetResponse],
        session_stream: AsyncSessionStream,
    ) -> None:
        """
        Orders should be sorted by placed_at in ascending order.
        """

        if not orders:
            logger.debug(f"No orders to process for contract {self.contract_id}")
            return
        logger.debug(f"Processing {len(orders)} orders for contract {self.contract_id}")

        sample_start_time = orders[0].placed_at
        sample_interval_in_seconds = self.sample_interval / 1000

        if len(orders) == 1:
            total_interval_in_seconds = Decimal(1)
            number_of_samples = 1
            sample_end_time = sample_start_time + timedelta(
                seconds=int(sample_interval_in_seconds)
            )
        else:
            total_interval_in_seconds = Decimal(
                str((orders[-1].placed_at - orders[0].placed_at).total_seconds())
            )
            number_of_samples = int(
                total_interval_in_seconds / sample_interval_in_seconds
            )
            sample_end_time = orders[-1].placed_at

        price_moments = []

        for _ in range(number_of_samples):
            logger.info(
                f"Number of samples for interval [{sample_start_time} - {sample_end_time}] seconds: {number_of_samples}"
            )

            sample_orders = [
                order
                for order in orders
                if order.placed_at >= sample_start_time
                and order.placed_at < sample_end_time
            ]

            if not sample_orders:
                continue

            # Calculate best bid and ask
            sample_best_bid, sample_best_ask = min_and_max_price_for_limit_orders(
                sample_orders
            )

            # Assume market orders have an effective price equal to the best bid or ask
            # TODO: Check if this is correct
            for order in sample_orders:
                if order.type == "market":
                    order.price = (
                        sample_best_bid if order.side == "buy" else sample_best_ask
                    )

            # Calculate volume and price based on the sample interval
            sample_volume = sum(order.quantity for order in sample_orders)
            sample_price = (
                sum(
                    order.price * order.quantity
                    for order in sample_orders
                    if order.price is not None
                )
                / sample_volume
            )

            price_moments = {
                "timestamp": sample_start_time,
                "price": float(sample_price),
                "volume": float(sample_volume),
                "best_bid": float(sample_best_bid),
                "best_ask": float(sample_best_ask),
            }

            sample_start_time = sample_start_time + timedelta(
                seconds=int(sample_interval_in_seconds)
            )

            if not price_moments:
                logger.info("No price moments to trigger state update")
                continue

            await self.update_state(
                session_stream=session_stream,
                price_moments=price_moments,
            )
        logger.info(f"Processed {len(orders)} orders for contract {self.contract_id}")

    async def update_state(
        self,
        session_stream: AsyncSessionStream,
        price_moments: dict,
    ):
        logger.info("Updating state and strategy")

        # Update price moments
        async with session_stream() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO price_moments (
                        timestamp,
                        price,
                        volume,
                        best_bid,
                        best_ask
                    )
                    VALUES (
                        :timestamp,
                        :price,
                        :volume,
                        :best_bid,
                        :best_ask
                    )
                    """
                ),
                price_moments,
            )
            await session.commit()

        # TODO: Update strategy. Issue #22

    async def run(self) -> None:
        logger.info(f"Starting exchange bot for contract {self.contract_id}")

        poll_interval_in_seconds = self.poll_interval / 1000

        start_time = self.last_processed_order_timestamp
        end_time = datetime.now(timezone.utc)

        orders_in_exchange = await self.get_orders(
            contract_id=self.contract_id,
            start_time=start_time,
            end_time=end_time,
        )

        # For audit only
        if orders_in_exchange:
            self.last_processed_order_timestamp = orders_in_exchange[-1].placed_at

        while True:
            logger.debug(
                f"Orders in exchange until {self.last_processed_order_timestamp}: {len(orders_in_exchange)}"
            )
            await self.process_orders(orders=orders_in_exchange, session_stream=db())
            await asyncio.sleep(int(poll_interval_in_seconds))

            end_time = datetime.now(timezone.utc)

            orders_in_exchange = await self.get_orders(
                contract_id=self.contract_id,
                start_time=start_time,
                end_time=end_time,
            )

            # For audit only
            if orders_in_exchange:
                self.last_processed_order_timestamp = orders_in_exchange[-1].placed_at

    async def close(self) -> None:
        await self.exchange_client.aclose()


def min_and_max_price_for_limit_orders(
    orders: list[OrderGetResponse],
) -> tuple[Decimal, Decimal]:
    limit_bids = [
        order.price
        for order in orders
        if order.type == "limit" and order.side == "buy" and order.price is not None
    ]
    limit_asks = [
        order.price
        for order in orders
        if order.type == "limit" and order.side == "sell" and order.price is not None
    ]

    min_limit_bid = min(limit_bids) if limit_bids else Decimal(0.00)
    max_limit_ask = max(limit_asks) if limit_asks else Decimal(0.00)

    return min_limit_bid, max_limit_ask
