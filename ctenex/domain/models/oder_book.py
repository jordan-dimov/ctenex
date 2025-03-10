from collections import defaultdict
from typing import List, Optional
from uuid import UUID

from sortedcontainers import SortedDict

from ctenex.domain.models.order import Order
from ctenex.domain.models.trade import Trade


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
        self.orders_by_id = {}

    def add_order(self, order: Order) -> List[Trade]:
        """
        Add an order to the order book.

        For limit orders, add to the appropriate side if it doesn't match immediately.
        For market orders, match against existing orders immediately.

        Returns a list of trades that were executed.
        """
        # Implementation logic here...
        return []

    def cancel_order(self, order_id: UUID) -> Optional[Order]:
        """Cancel an order and remove it from the order book."""
        ...
