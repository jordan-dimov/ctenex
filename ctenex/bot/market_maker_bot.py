import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Callable
from uuid import UUID

import httpx
from loguru import logger

from ctenex.bot.orders_generators.basic import orders_generator
from ctenex.domain.entities import OrderSide, OrderType
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderAddResponse,
    OrderGetResponse,
)
from ctenex.settings.application import get_app_settings
from ctenex.utils.contracts import validate_contract_id

settings = get_app_settings()


BOT_TRADER_ID = UUID("c4adb8ee-1425-4a10-bd10-87dd587670d3")


class InternalStateError(Exception): ...


class MatchingBot:
    def __init__(
        self,
        trader_id: UUID,
        contract_id: str,
        base_url: str,
        poll_interval: float = 1.0,
        poll_size: int = 5,
        number_of_orders: int = 2,
        orders_generator: Callable = orders_generator,
    ):
        # Configuration
        self.base_url = base_url
        self.trader_id = trader_id
        self.contract_id = contract_id
        self.poll_interval = poll_interval
        self.poll_size = poll_size
        self.number_of_orders = number_of_orders

        # Dependencies
        self.exchange_client = httpx.AsyncClient(base_url=base_url)
        self.orders_generator = orders_generator

        # State
        self.last_processed_order_timestamp: datetime = datetime.now()
        self.mid_price: Decimal = Decimal(0.00)
        self.best_bid: Decimal = Decimal(0.00)
        self.best_ask: Decimal = Decimal(0.00)
        self.best_bid_quantity: Decimal = Decimal(0.00)
        self.best_ask_quantity: Decimal = Decimal(0.00)
        self.tick_size: Decimal = Decimal(0.00)
        self.spread: Decimal = Decimal(0.00)

    async def validate_contract_id(self, contract_id: str) -> None:
        contracts = validate_contract_id(contract_id, self.base_url)
        self.tick_size = next(
            (c.tick_size for c in contracts if c.contract_id == contract_id),
            Decimal(0.00),
        )

    async def get_orders(self, contract_id: str, status: str) -> list[OrderGetResponse]:
        logger.info(f"Polling {status} orders for contract {contract_id}")

        response = await self.exchange_client.get(
            url="/v1/stateless/orders",
            params={
                "contract_id": contract_id,
                "status": status,
                "limit": self.poll_size,
                "page": 1,
            },
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

    async def process_orders(self, orders: list[OrderGetResponse], status: str) -> None:
        if not orders:
            logger.info("No orders to process")
            return

        logger.info(
            f"Processing {len(orders)} {status} order(s) for contract {self.contract_id}"
        )

        for order in orders:
            # Skip our own orders or already processed orders
            if order.trader_id == self.trader_id:
                continue

            # TODO: Handle market orders
            # Market orders sound like the ideal opportunity to make a profit.
            # How do we make sure the bot offers a fair price even for market orders?
            order_price = order.price if order.price is not None else self.mid_price
            if order.type == OrderType.MARKET and order.price is None:
                continue

            # Update state for order price and quantity decision
            order_quantity = (
                order.remaining_quantity
                if order.remaining_quantity is not None
                else order.quantity
            )

            self.update_state(
                price=order_price,
                side=order.side,
                quantity=order_quantity,
            )

            # Generate orders around the mid-price and considering the spread
            generated_orders = self.orders_generator(
                contract_id=self.contract_id,
                trader_id=self.trader_id,
                number_of_orders=self.number_of_orders,
                side=order.side,
                price=self.mid_price,
                tick_size=self.tick_size,
                spread=self.spread,
            )

            # Place orders
            for generated_order in generated_orders:
                try:
                    await self.place_order(generated_order)
                    self.last_processed_order_timestamp = datetime.now()
                except Exception as e:
                    logger.error(f"Failed to place matching order: {e}")

    def update_state(
        self,
        price: Decimal,
        side: OrderSide,
        quantity: Decimal,
    ) -> None:
        if side == OrderSide.BUY and price > self.best_bid:
            self.best_bid = price
            self.best_bid_quantity = quantity
        elif side == OrderSide.SELL and (
            price < self.best_ask or self.best_ask == Decimal(0.00)
        ):
            self.best_ask = price
            self.best_ask_quantity = quantity

        if self.best_bid == Decimal(0.00):
            self.mid_price = self.best_ask
        elif self.best_ask == Decimal(0.00):
            self.mid_price = self.best_bid
        else:
            self.mid_price = (self.best_bid + self.best_ask) / 2
            self.spread = abs(self.best_ask - self.best_bid)

    async def run(self) -> None:
        logger.info(f"Starting matching bot for contract {self.contract_id}")
        while True:
            open_orders = await self.get_orders(
                self.contract_id,
                status="open",
            )

            open_orders = [
                order for order in open_orders if order.trader_id != self.trader_id
            ]
            await self.process_orders(open_orders, status="open")

            partially_filled_orders = await self.get_orders(
                self.contract_id,
                status="partially_filled",
            )
            partially_filled_orders = [
                order
                for order in partially_filled_orders
                if order.trader_id != self.trader_id
            ]
            await self.process_orders(
                partially_filled_orders, status="partially_filled"
            )

            await asyncio.sleep(self.poll_interval)
            # break

    async def close(self) -> None:
        await self.exchange_client.aclose()


async def main():
    bot = MatchingBot(
        trader_id=BOT_TRADER_ID,
        base_url=str(settings.api.base_url),
        contract_id="UK-BL-MAR-25",
    )
    try:
        await bot.validate_contract_id("UK-BL-MAR-25")
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
