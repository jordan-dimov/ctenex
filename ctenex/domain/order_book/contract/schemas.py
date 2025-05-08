from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ContractGetResponse(BaseModel):
    contract_id: str
    commodity: str
    delivery_period: str
    start_date: datetime
    end_date: datetime
    tick_size: Decimal
    contract_size: Decimal
    location: str
