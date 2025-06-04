from decimal import Decimal

from pydantic import field_validator

from ctenex.core.utils.filter_sort import BaseFilterParams
from ctenex.core.utils.validators import validate_enum
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

    @field_validator("status", "side", "type")
    def validate_enum(cls, v):
        return validate_enum(v)
