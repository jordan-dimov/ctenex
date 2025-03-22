from datetime import datetime
from enum import Enum

from ctenex.domain.contract.model import Commodity, Contract, DeliveryPeriod


class ContractCode(str, Enum):
    UK_BL_MAR_25 = "UK-BL-MAR-25"


class ContractBaselineMarch2025(Contract):
    id: str = ContractCode.UK_BL_MAR_25
    commodity: Commodity = Commodity.POWER
    delivery_period: DeliveryPeriod = DeliveryPeriod.MONTHLY
    start_date: datetime = datetime(2025, 3, 1)
    end_date: datetime = datetime(2025, 3, 31)
    location: str = "GB"
    tick_size: float = 0.01
    contract_size: float = 1.0
