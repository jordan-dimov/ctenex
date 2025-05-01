from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ctenex.domain.order_book.trade.model import Trade


class TestTrade:
    def test_trade_creation(self):
        trade = Trade(
            contract_id="UK-POWER-MAR-2025",
            buy_order_id=UUID("a15e9c9f-8dce-4ae0-8a7a-5ca1aa0498e2"),
            sell_order_id=UUID("b23f8d7e-5c1a-4b89-9d2e-7a5fb1234567"),
            price=Decimal("152.25"),
            quantity=Decimal("3.0"),
        )

        assert trade.contract_id == "UK-POWER-MAR-2025"
        assert trade.buy_order_id == UUID("a15e9c9f-8dce-4ae0-8a7a-5ca1aa0498e2")
        assert trade.sell_order_id == UUID("b23f8d7e-5c1a-4b89-9d2e-7a5fb1234567")
        assert trade.price == Decimal("152.25")
        assert trade.quantity == Decimal("3.0")
        assert isinstance(trade.generated_at, datetime)
