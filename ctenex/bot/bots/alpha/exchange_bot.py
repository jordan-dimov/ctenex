import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

import httpx
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import text

from ctenex.bot.db.async_session import AsyncSessionStream, db
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderAddResponse,
    OrderGetResponse,
)
from ctenex.utils.contracts import validate_contract_id


class ProcessingResult(BaseModel):
    number_of_orders_processed: int
    last_processed_order_timestamp: datetime | None = None


class ExchangeBot:
    def __init__(
        self,
        trader_id: UUID,
        contract_id: str,
        base_url: str,
        sample_interval_in_ms: Decimal = Decimal(1000.0),
        base_drift_in_ms: Decimal = Decimal(1100.0),
    ):
        """
        Args:
            trader_id: The trader ID.
            contract_id: The contract ID.
            base_url: The base URL of the exchange.
            sample_interval_in_ms: The interval between samples.
            base_drift_in_ms: The base drift in milliseconds.

        The sample interval is a fixed time interval used to filter the orders when querying.
        Each query issued fetches orders placed within the sample interval. This is effectively
        used to calculate the value for the `placed_before` filter from the value of the
        `placed_at_or_after` filter.

        The base drift is the difference between the real time at which an orders query is issued and
        the time used to filter orders (i.e. the value used for the `placed_at_or_after` filter).
        """

        # Configuration
        self.base_url = base_url
        self.trader_id = trader_id
        self.contract_id = contract_id
        self.sample_interval_in_ms = sample_interval_in_ms
        self.base_drift_in_ms = base_drift_in_ms
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
        """
        Get the orders for the given contract.

        Args:
            contract_id: The contract ID.
            start_time: The start time of the interval.
            end_time: The end time of the interval.
        """

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
        """
        Place an order on the exchange.

        Args:
            order: The order to place.
        """

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
    ) -> ProcessingResult:
        """
        Process the orders for the given contract.

        Args:
            orders: The orders to process (sorted by `placed_at` in ascending order).
            session_stream: A session stream to persist the state changes.
        """

        processing_result = ProcessingResult(
            number_of_orders_processed=0,
            last_processed_order_timestamp=None,
        )

        if not orders:
            logger.debug(f"No orders to process for contract {self.contract_id}")
            return processing_result

        first_order_timestamp = orders[0].placed_at
        last_order_timestamp = orders[-1].placed_at

        logger.debug(
            f"Processing {len(orders)} orders for contract {self.contract_id}. "
            f"Batch interval: [{first_order_timestamp} - {last_order_timestamp}]"
        )

        price_moments = []

        # Calculate best bid and ask
        best_bid, best_ask = best_bid_and_ask_for_limit_orders(orders)

        # Assume market orders have an effective price equal to the best bid or ask
        # TODO: Check if this assumption is correct
        for order in orders:
            if order.type == "market":
                order.price = best_bid if order.side == "buy" else best_ask

        # Calculate volume and price based on the sample interval
        sample_volume = sum(order.quantity for order in orders)
        sample_price = (
            sum(
                order.price * order.quantity
                for order in orders
                if order.price is not None
            )
            / sample_volume
        )

        price_moments = {
            "timestamp": first_order_timestamp,
            "price": float(sample_price),
            "volume": float(sample_volume),
            "best_bid": float(best_bid),
            "best_ask": float(best_ask),
        }

        await self.update_state(
            session_stream=session_stream,
            price_moments=price_moments,
        )

        processing_result.number_of_orders_processed = len(orders)
        processing_result.last_processed_order_timestamp = last_order_timestamp

        logger.info(
            f"Processed {processing_result.number_of_orders_processed} orders for contract {self.contract_id}. "
            f"Interval: [{first_order_timestamp} - {last_order_timestamp}]"
        )

        return processing_result

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

        current_timestamp = datetime.now(timezone.utc)
        start_timestamp = current_timestamp - timedelta(
            milliseconds=int(self.base_drift_in_ms)
        )
        end_timestamp = start_timestamp + timedelta(
            milliseconds=int(self.sample_interval_in_ms)
        )

        logger.debug(
            f"Getting orders for interval [{start_timestamp} - {end_timestamp}]"
        )
        orders_in_exchange = await self.get_orders(
            contract_id=self.contract_id,
            start_time=start_timestamp,
            end_time=end_timestamp,
        )

        while True:
            await self.process_orders(orders=orders_in_exchange, session_stream=db())

            current_timestamp = datetime.now(timezone.utc)

            start_timestamp = end_timestamp
            end_timestamp = start_timestamp + timedelta(
                milliseconds=int(self.sample_interval_in_ms)
            )
            drift_error_in_ms = (current_timestamp - start_timestamp) / timedelta(
                milliseconds=1
            )

            ### Use the error to adjust the period and keep the drift constant
            real_drift_in_ms = int(self.base_drift_in_ms) - drift_error_in_ms
            adjusted_period_in_millis = real_drift_in_ms - drift_error_in_ms
            # logger.debug(
            #     f"Real drift in ms: {real_drift_in_ms}. "
            #     f"Drift error in ms: {drift_error_in_ms}. "
            #     f"Adjusted period in ms: {adjusted_period_in_millis}"
            # )
            await asyncio.sleep(adjusted_period_in_millis / 1000)

            logger.debug(
                f"Getting orders for interval [{start_timestamp} - {end_timestamp}]"
            )
            orders_in_exchange = await self.get_orders(
                contract_id=self.contract_id,
                start_time=start_timestamp,
                end_time=end_timestamp,
            )

    async def close(self) -> None:
        await self.exchange_client.aclose()


def best_bid_and_ask_for_limit_orders(
    orders: list[OrderGetResponse],
) -> tuple[Decimal, Decimal]:
    """
    Calculate the minimum and maximum price from the limit orders.
    """

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

    best_bid = max(limit_bids) if limit_bids else Decimal(0.00)
    best_ask = min(limit_asks) if limit_asks else Decimal(0.00)

    return best_bid, best_ask
