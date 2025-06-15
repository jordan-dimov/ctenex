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
    RANDOM_TICKS_FACTOR = 2  # Stay close to mid-price
    MIN_PROFIT_TICKS = 1  # Minimum number of ticks we want to profit from spread

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

        # Calculate minimum profitable price difference
        min_profit = tick_size * Decimal(BasicOrdersGenerator.MIN_PROFIT_TICKS)

        for i in range(number_of_orders):
            if i == 0:
                # For the first order, we want to match the incoming order
                # but ensure we're on the profitable side of the spread
                if side == OrderSide.BUY:
                    # If someone wants to buy, we sell at a higher price
                    matching_side = OrderSide.SELL
                    order_price = price + min_profit
                else:
                    # If someone wants to sell, we buy at a lower price
                    matching_side = OrderSide.BUY
                    order_price = price - min_profit
            else:
                # For subsequent orders, we place orders around the mid-price
                # but always ensuring we're on the profitable side of the spread
                if randrange(2) == 0:
                    # Place a sell order above mid-price
                    matching_side = OrderSide.SELL
                    order_price = price + tick_size * Decimal(
                        randrange(
                            BasicOrdersGenerator.MIN_PROFIT_TICKS,
                            BasicOrdersGenerator.RANDOM_TICKS_FACTOR,
                        )
                    )
                else:
                    # Place a buy order below mid-price
                    matching_side = OrderSide.BUY
                    order_price = price - tick_size * Decimal(
                        randrange(
                            BasicOrdersGenerator.MIN_PROFIT_TICKS,
                            BasicOrdersGenerator.RANDOM_TICKS_FACTOR,
                        )
                    )

            # Scale quantity based on spread - larger spreads get larger orders
            if spread == Decimal(0.00):
                order_quantity = Decimal(1.00)
            else:
                # Scale quantity based on spread size, but cap it
                order_quantity = min(spread * Decimal(2), Decimal(10.00))

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
