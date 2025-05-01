from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import OpenOrderStatus, OrderSide, OrderType
from ctenex.domain.order_book.order.model import Order


class TestOrder:
    def test_order_creation(self):
        order = Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("a0130b4b-5f77-4703-9a18-1af5a87cc8eb"),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("152.50"),
            quantity=Decimal("5.0"),
            remaining_quantity=Decimal("5.0"),
        )

        assert isinstance(order.id, UUID)
        assert order.contract_id == ContractCode.UK_BL_MAR_25
        assert order.trader_id == UUID("a0130b4b-5f77-4703-9a18-1af5a87cc8eb")
        assert order.side == OrderSide.BUY
        assert order.type == OrderType.LIMIT
        assert order.price == Decimal("152.50")
        assert order.quantity == Decimal("5.0")
        assert isinstance(order.placed_at, datetime)
        assert order.status == OpenOrderStatus.OPEN
        assert order.remaining_quantity == Decimal("5.0")
