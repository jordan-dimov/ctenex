from decimal import Decimal
from random import randrange
from uuid import UUID

from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderSide,
    OrderType,
)

RANDOM_TICKS_FACTOR = 3  # TODO: increase complexity


def orders_generator(
    contract_id: str,
    trader_id: UUID,
    number_of_orders: int,
    price: Decimal,
    tick_size: Decimal,
    spread: Decimal,
) -> list[OrderAddRequest]:
    orders = []
    for _ in range(number_of_orders):
        order_price = price + tick_size * Decimal(
            randrange(-RANDOM_TICKS_FACTOR, RANDOM_TICKS_FACTOR)
        )
        matching_side = OrderSide.SELL if randrange(2) == 0 else OrderSide.BUY

        matching_order = OrderAddRequest(
            contract_id=contract_id,
            trader_id=trader_id,
            side=matching_side,
            type=OrderType.LIMIT,
            price=order_price,
            quantity=spread,  # TODO: increase complexity
        )
        orders.append(matching_order)
    return orders
