from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from ctenex.domain.base_model import BaseDomainModel
from ctenex.domain.entities import Commodity, DeliveryPeriod


class Contract(BaseDomainModel):
    external_id: str = Field(description="Unique identifier for the contract")
    commodity: Commodity
    delivery_period: DeliveryPeriod
    start_date: datetime
    end_date: datetime
    location: str = Field(description="Delivery location code (e.g., 'GB', 'DE')")
    tick_size: Decimal = Field(description="Minimum price movement")
    contract_size: Decimal = Field(
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
