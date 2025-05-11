from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from ctenex.domain.entities import OrderSide, OrderStatus, OrderType


class OrderAddRequest(BaseModel):
    contract_id: str
    trader_id: UUID
    side: OrderSide
    type: OrderType
    price: Decimal | None = None
    quantity: Decimal


class OrderAddResponse(BaseModel):
    id: UUID
    contract_id: str
    trader_id: UUID
    side: OrderSide
    type: OrderType
    price: Decimal | None = None
    quantity: Decimal
    status: OrderStatus


class OrderGetResponse(BaseModel):
    id: UUID
    contract_id: str
    trader_id: UUID
    side: OrderSide
    type: OrderType
    price: Decimal | None = None
    quantity: Decimal
    status: OrderStatus
    remaining_quantity: Decimal | None = None
    placed_at: datetime
