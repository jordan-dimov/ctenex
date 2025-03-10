from datetime import datetime
from uuid import UUID

from ctenex.domain.models.trade import Trade


class TestTrade:
    def test_trade_creation(self):
        trade = Trade(
            contract_id="UK-POWER-MAR-2025",
            buy_order_id=UUID("a15e9c9f-8dce-4ae0-8a7a-5ca1aa0498e2"),
            sell_order_id=UUID("b23f8d7e-5c1a-4b89-9d2e-7a5fb1234567"),
            price=152.25,
            quantity=3.0,
        )

        assert trade.contract_id == "UK-POWER-MAR-2025"
        assert trade.buy_order_id == UUID("a15e9c9f-8dce-4ae0-8a7a-5ca1aa0498e2")
        assert trade.sell_order_id == UUID("b23f8d7e-5c1a-4b89-9d2e-7a5fb1234567")
        assert trade.price == 152.25
        assert trade.quantity == 3.0
        assert isinstance(trade.timestamp, datetime)
