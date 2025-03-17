from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Trade(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    contract_id: str
    buy_order_id: UUID
    sell_order_id: UUID
    price: float
    quantity: float
    timestamp: datetime = Field(default=datetime.now(UTC))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contract_id": "UK-POWER-MAR-2025",
                "buy_order_id": "a15e9c9f-8dce-4ae0-8a7a-5ca1aa0498e2",
                "sell_order_id": "b23f8d7e-5c1a-4b89-9d2e-7a5fb1234567",
                "price": 152.25,
                "quantity": 3.0,
            }
        }
    )

    def __str__(self) -> str:
        return (
            "Trade(\n"
            f"id={self.id}\n"
            f"contract_id={self.contract_id}\n"
            f"buy_order_id={self.buy_order_id}\n"
            f"sell_order_id={self.sell_order_id}\n"
            f"price={self.price}\n"
            f"quantity={self.quantity}\n"
            f"timestamp={self.timestamp}\n"
            ")"
        )
