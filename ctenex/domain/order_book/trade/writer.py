from ctenex.core.data_access.writer import GenericWriter
from ctenex.domain.entities import Trade


class TradesWriter(GenericWriter[Trade]):
    model = Trade


trades_writer = TradesWriter()
