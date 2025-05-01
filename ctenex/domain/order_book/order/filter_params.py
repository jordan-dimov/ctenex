from decimal import Decimal

from ctenex.core.utils.filter_sort import BaseFilterParams
from ctenex.domain.entities import OrderSide, OrderStatus, OrderType


class OrderFilterParams(BaseFilterParams):
    """Filter parameters for orders."""

    contract_id: str | None = None
    trader_id: str | None = None
    side: OrderSide | None = None
    type: OrderType | None = None
    status: OrderStatus | None = None
    price: Decimal | None = None
    quantity: Decimal | None = None
