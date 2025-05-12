import asyncio
from uuid import UUID

import httpx
from loguru import logger

from ctenex.domain.entities import OrderSide
from ctenex.domain.order_book.order.schemas import OrderAddRequest, OrderGetResponse
from ctenex.settings.application import get_app_settings

settings = get_app_settings()

BOT_TRADER_ID = UUID("c4adb8ee-1425-4a10-bd10-87dd587670d3")

class MatchingBot:
    def __init__(
        self,
        trader_id: UUID,
        base_url: str,
        poll_interval: float = 1.0,
    ):
        self.base_url = base_url
        self.trader_id = trader_id
        self.poll_interval = poll_interval
        self.client = httpx.AsyncClient(base_url=base_url)
        self.processed_orders: set[UUID] = set()

    async def get_orders(self, contract_id: str) -> list[OrderGetResponse]:
        response = await self.client.get(
            url="/v1/stateless/orders",
            params={
                "contract_id": contract_id,
                "status": "OPEN",
                "limit": 5,
                "page": 1,
            },
        )
        response.raise_for_status()
        return [OrderGetResponse(**order) for order in response.json()]

    async def place_order(self, order: OrderAddRequest) -> None:
        response = await self.client.post(
            url="/v1/stateless/orders", json=order.model_dump(mode="json")
        )
        response.raise_for_status()
        logger.info(f"Placed order: {response.json()}")

    async def process_order(self, order: OrderGetResponse) -> None:
        if order.id in self.processed_orders:
            return

        # Skip our own orders
        if order.trader_id == self.trader_id:
            return

        # Create matching order
        matching_side = OrderSide.SELL if order.side == OrderSide.BUY else OrderSide.BUY
        matching_order = OrderAddRequest(
            contract_id=order.contract_id,
            trader_id=self.trader_id,
            side=matching_side,
            type=order.type,
            price=order.price,
            quantity=order.quantity,
        )

        try:
            await self.place_order(matching_order)
            self.processed_orders.add(order.id)
            logger.info(f"Matched order {order.id} with {matching_side} order")
        except Exception as e:
            logger.error(f"Failed to place matching order: {e}")

    async def run(self, contract_id: str) -> None:
        logger.info(f"Starting matching bot for contract {contract_id}")
        while True:
            try:
                orders = await self.get_orders(contract_id)
                for order in orders:
                    await self.process_order(order)
            except Exception as e:
                logger.error(f"Error in bot loop: {e}")

            await asyncio.sleep(self.poll_interval)

    async def close(self) -> None:
        await self.client.aclose()


async def main():
    logger.info("Starting matching bot")
    bot = MatchingBot(trader_id=BOT_TRADER_ID, base_url=str(settings.api.base_url))
    try:
        await bot.run("UK-BL-MAR-25")
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
