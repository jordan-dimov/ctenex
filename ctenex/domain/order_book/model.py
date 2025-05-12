from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select

from ctenex.core.db.async_session import AsyncSessionStream, get_async_session
from ctenex.core.db.utils import get_entity_values
from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import Order, OrderSide, OrderType, ProcessedOrderStatus
from ctenex.domain.order_book.order.model import Order as OrderSchema
from ctenex.domain.order_book.order.reader import OrderFilter, orders_reader
from ctenex.domain.order_book.order.writer import orders_writer


class OrderBook:
    orders_writer = orders_writer
    orders_reader = orders_reader

    def __init__(
        self,
        db: AsyncSessionStream = get_async_session,
    ):
        self.db: AsyncSessionStream = db

    async def get_orders(
        self,
        filter: OrderFilter,
        limit: int = 10,
        page: int = 1,
    ) -> list[OrderSchema]:
        orders = await self.orders_reader.get_many(
            self.db,
            filter=filter,
            limit=limit,
            page=page,
        )
        return [OrderSchema(**get_entity_values(order)) for order in orders]

    async def get_order(
        self,
        order_id: UUID,
    ) -> OrderSchema | None:
        order = await self.orders_reader.get(self.db, order_id)
        if order is None:
            return None

        return OrderSchema(**get_entity_values(order))

    async def add_order(self, order: OrderSchema) -> UUID:
        """Add an order to the appropriate side of the book."""

        # For market orders, set price to MAX (buy) or 0 (sell) to ensure matching
        if order.type == OrderType.MARKET:
            order.price = (
                Decimal("999.99") if order.side == OrderSide.BUY else Decimal("0.00")
            )
        elif order.price is None:
            raise ValueError("Order must have a price")

        async with self.db() as session:
            entity = Order(**order.model_dump())
            await self.orders_writer.create(session, entity)
            await session.commit()

        return entity.id

    async def cancel_order(self, order_id: UUID) -> OrderSchema | None:
        """Cancel an order and remove it from the book."""

        entity = await self.orders_reader.get(self.db, order_id)
        if entity is None:
            return None

        if entity.price is None:
            raise ValueError("Order cannot be cancelled as it has no price")

        entity.status = ProcessedOrderStatus.CANCELLED
        async with self.db() as session:
            await self.orders_writer.update(session, entity)
            await session.commit()

        return OrderSchema(**get_entity_values(entity))

    async def update_order(self, order: OrderSchema) -> OrderSchema:
        """Update an order in the order book."""
        async with self.db() as session:
            entity = Order(**order.model_dump())
            await self.orders_writer.update(session, entity)
            await session.commit()

        return OrderSchema(**get_entity_values(entity))

    async def get_best_ask_price(
        self,
        contract_id: ContractCode,
    ) -> Decimal | None:
        """Get the best ask price from the order book."""
        async with self.db() as session:
            best_ask = await session.execute(
                select(func.max(Order.price)).where(
                    Order.contract_id == contract_id,
                    Order.side == OrderSide.SELL,
                )
            )
            return best_ask.scalar_one_or_none()

    async def get_best_bid_price(
        self,
        contract_id: ContractCode,
    ) -> Decimal | None:
        """Get the best bid price from the order book."""
        async with self.db() as session:
            best_bid = await session.execute(
                select(func.min(Order.price)).where(
                    Order.contract_id == contract_id,
                    Order.side == OrderSide.BUY,
                )
            )
            return best_bid.scalar_one_or_none()


order_book = OrderBook()
