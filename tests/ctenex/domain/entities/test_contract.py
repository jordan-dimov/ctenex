from datetime import datetime
from decimal import Decimal

from ctenex.domain.entities import Commodity, DeliveryPeriod
from ctenex.domain.order_book.contract.model import Contract


class TestContract:
    def test_contract_creation(self):
        contract = Contract(
            external_id="UK-POWER-MAR-2025",
            commodity=Commodity.POWER,
            delivery_period=DeliveryPeriod.MONTHLY,
            start_date=datetime(2025, 3, 1),
            end_date=datetime(2025, 3, 31),
            location="GB",
            tick_size=Decimal("0.01"),
            contract_size=Decimal("1.0"),
        )

        assert contract.external_id == "UK-POWER-MAR-2025"
        assert contract.commodity == "power"
        assert contract.delivery_period == "monthly"
        assert contract.start_date == datetime(2025, 3, 1)
        assert contract.end_date == datetime(2025, 3, 31)
        assert contract.location == "GB"
        assert contract.tick_size == Decimal("0.01")
        assert contract.contract_size == Decimal("1.0")
