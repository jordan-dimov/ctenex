from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(str, Enum):
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    contract_id: str
    trader_id: str
    side: OrderSide
    order_type: OrderType
    price: float | None = Field(
        default=None, description="Required for limit orders, ignored for market orders"
    )
    quantity: float
    remaining_quantity: float | None = Field(default=None)
    created_at: datetime = Field(default=datetime.now(UTC))
    status: OrderStatus = Field(default=OrderStatus.OPEN)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contract_id": "UK-POWER-MAR-2025",
                "trader_id": "trader123",
                "side": "buy",
                "order_type": "limit",
                "price": 152.50,
                "quantity": 5.0,
            }
        }
    )
