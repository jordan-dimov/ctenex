from decimal import Decimal
from random import randrange
from uuid import UUID

from ctenex.bot.orders_generators.interface import IOrdersGenerator
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderSide,
    OrderType,
)


class BasicOrdersGenerator(IOrdersGenerator):
    RANDOM_TICKS_FACTOR = 3  # TODO: increase complexity

    def generate_orders(
        self,
        contract_id: str,
        trader_id: UUID,
        side: OrderSide,
        price: Decimal,
        tick_size: Decimal,
        spread: Decimal,
        number_of_orders: int = 3,
    ) -> list[OrderAddRequest]:
        orders = []

        for i in range(number_of_orders):
            # First "match" the order with a profit margin equal to the tick size
            if i == 0:
                matching_side = (
                    OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
                )
                profit_margin = tick_size if side == OrderSide.BUY else -tick_size
                order_price = price + profit_margin
            # Then generate orders around the mid-price
            else:
                matching_side = OrderSide.SELL if randrange(2) == 0 else OrderSide.BUY
                order_price = price + tick_size * Decimal(
                    randrange(
                        -BasicOrdersGenerator.RANDOM_TICKS_FACTOR,
                        BasicOrdersGenerator.RANDOM_TICKS_FACTOR,
                    )
                )

            if spread == Decimal(0.00):
                order_quantity = Decimal(1.00)
            else:
                order_quantity = spread

            matching_order = OrderAddRequest(
                contract_id=contract_id,
                trader_id=trader_id,
                side=matching_side,
                type=OrderType.LIMIT,
                price=order_price,
                quantity=order_quantity,
            )
            orders.append(matching_order)
        return orders
