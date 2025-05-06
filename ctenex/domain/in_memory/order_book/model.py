from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from sortedcontainers import SortedDict

from ctenex.domain.entities import OrderSide, OrderType, ProcessedOrderStatus
from ctenex.domain.order_book.order.model import Order


class OrderBook:
    def __init__(self, contract_id: str):
        self.contract_id = contract_id

        # Buy orders sorted by price (descending) and then by time (ascending)
        # SortedDict with negative price as key for descending sort
        self.bids = SortedDict()

        # Sell orders sorted by price (ascending) and then by time (ascending)
        self.asks = SortedDict()

        # Time-based queues at each price level
        self.bid_queues = defaultdict(list)  # price -> list of orders
        self.ask_queues = defaultdict(list)  # price -> list of orders

        # Fast lookup for orders by ID
        self.orders_by_id: dict[UUID, Order] = {}

    def get_orders(self) -> list[Order]:
        return list(self.orders_by_id.values())

    def add_order(self, order: Order) -> UUID:
        """Add an order to the appropriate side of the book."""

        # For market orders, set price to infinity (buy) or 0 (sell) to ensure matching
        if order.type == OrderType.MARKET:
            order.price = (
                Decimal("999.99") if order.side == OrderSide.BUY else Decimal("0.00")
            )
        elif order.price is None:
            raise ValueError("Order must have a price")

        self.orders_by_id[order.id] = order

        if order.side == OrderSide.BUY:
            # Store negative price for descending sort
            self.bids[-order.price] = True
            self.bid_queues[order.price].append(order)
        else:
            self.asks[order.price] = True
            self.ask_queues[order.price].append(order)

        return order.id

    def cancel_order(self, order_id: UUID) -> Order | None:
        """Cancel an order and remove it from the book."""
        if order_id not in self.orders_by_id:
            return None

        order = self.orders_by_id[order_id]

        if order.price is None:
            raise ValueError("Order cannot be cancelled as it has no price")

        # Remove from price queue
        if order.side == OrderSide.BUY:
            self.bid_queues[order.price].remove(order)
            if not self.bid_queues[order.price]:
                del self.bid_queues[order.price]
                del self.bids[-order.price]
        else:
            self.ask_queues[order.price].remove(order)
            if not self.ask_queues[order.price]:
                del self.ask_queues[order.price]
                del self.asks[order.price]

        # Remove from ID lookup
        del self.orders_by_id[order_id]

        order.status = ProcessedOrderStatus.CANCELLED
        return order
