from uuid import UUID

from pydantic import BaseModel

from ctenex.domain.order.model import OrderSide, OrderStatus, OrderType


class OrderAddRequest(BaseModel):
    contract_id: str
    trader_id: str
    side: OrderSide
    order_type: OrderType
    price: float | None = None
    quantity: float


class OrderAddResponse(BaseModel):
    id: UUID
    contract_id: str
    trader_id: str
    side: OrderSide
    order_type: OrderType
    price: float | None = None
    quantity: float
    status: OrderStatus
