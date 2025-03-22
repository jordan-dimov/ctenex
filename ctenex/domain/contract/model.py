from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Commodity(str, Enum):
    POWER = "power"
    NATURAL_GAS = "natural_gas"
    CRUDE_OIL = "crude_oil"


class DeliveryPeriod(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Contract(BaseModel):
    id: str = Field(description="Unique identifier for the contract")
    commodity: Commodity
    delivery_period: DeliveryPeriod
    start_date: datetime
    end_date: datetime
    location: str = Field(description="Delivery location code (e.g., 'GB', 'DE')")
    tick_size: float = Field(description="Minimum price movement")
    contract_size: float = Field(
        description="Size of one contract unit in MW or equivalent"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "UK-POWER-MAR-2025",
                "commodity": "power",
                "delivery_period": "monthly",
                "start_date": "2025-03-01T00:00:00",
                "end_date": "2025-03-31T23:59:59",
                "location": "GB",
                "tick_size": 0.01,
                "contract_size": 1.0,
            }
        }
    )
