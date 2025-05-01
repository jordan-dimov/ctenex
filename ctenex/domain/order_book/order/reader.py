from ctenex.core.data_access.reader import GenericReader
from ctenex.domain.entities import Order
from ctenex.domain.order_book.order.filter_params import OrderFilterParams


class OrderFilter(OrderFilterParams):
    """Filter parameters for Book orders."""


class OrdersReader(GenericReader[Order]):
    """Reader for Book orders."""

    model = Order


orders_reader = OrdersReader()
