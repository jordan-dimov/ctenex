from datetime import datetime
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
    placed_at_or_after: datetime | None = None
    placed_before: datetime | None = None

    @field_validator("placed_before")
    def validate_placed_before(cls, v, values):
        placed_at_or_after = values.data.get("placed_at_or_after")

        if placed_at_or_after and v and placed_at_or_after >= v:
            raise ValueError("Placed before must be after placed at or after")
        return v

    @field_validator("status", "side", "type")
    def validate_enum(cls, v):
        return validate_enum(v)
