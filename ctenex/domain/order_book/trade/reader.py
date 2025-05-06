from ctenex.core.data_access.reader import GenericReader
from ctenex.domain.entities import Trade
from ctenex.domain.order_book.trade.filter_params import TradeFilterParams


class TradeFilter(TradeFilterParams):
    """Filter parameters for Book trades."""


class TradesReader(GenericReader[Trade]):
    """Reader for Book trades."""

    model = Trade


trades_reader = TradesReader()
