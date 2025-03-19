from datetime import datetime
from uuid import UUID

from ctenex.domain.contract_codes import ContractCode
from ctenex.domain.order.model import Order, OrderSide, OrderStatus, OrderType


class TestOrder:
    def test_order_creation(self):
        order = Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="trader123",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=152.50,
            quantity=5.0,
            remaining_quantity=5.0,
        )

        assert isinstance(order.id, UUID)
        assert order.contract_id == ContractCode.UK_BL_MAR_25
        assert order.trader_id == "trader123"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.price == 152.50
        assert order.quantity == 5.0
        assert isinstance(order.created_at, datetime)
        assert order.status == OrderStatus.OPEN
        assert order.remaining_quantity == 5.0
