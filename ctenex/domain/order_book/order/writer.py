from ctenex.core.data_access.writer import GenericWriter
from ctenex.domain.entities import Order


class OrdersWriter(GenericWriter[Order]):
    model = Order


orders_writer = OrdersWriter()
