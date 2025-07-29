from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ctenex.domain.entities import OrderSide
from ctenex.domain.order_book.order.schemas import OrderAddRequest


class IOrdersGenerator(Protocol):
    def generate_orders(
        self,
        contract_id: str,
        trader_id: UUID,
        side: OrderSide,
        price: Decimal,
        tick_size: Decimal,
        spread: Decimal,
        number_of_orders: int = 3,
    ) -> list[OrderAddRequest]: ...
