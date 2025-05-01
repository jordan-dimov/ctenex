from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from ctenex.domain.base_model import BaseDomainModel
from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import (
    OpenOrderStatus,
    OrderSide,
    OrderStatus,
    OrderType,
)


class Order(BaseDomainModel):
    contract_id: ContractCode
    trader_id: UUID
    side: OrderSide
    type: OrderType
    price: Decimal | None = Field(
        default=None, description="Required for limit orders, ignored for market orders"
    )
    quantity: Decimal
    status: OrderStatus = Field(default=OpenOrderStatus.OPEN)
    remaining_quantity: Decimal | None = Field(default=None)
    placed_at: datetime = Field(default=datetime.now(UTC))
