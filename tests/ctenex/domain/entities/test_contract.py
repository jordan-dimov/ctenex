from datetime import datetime

from ctenex.domain.entities.contract.model import Commodity, Contract, DeliveryPeriod


class TestContract:
    def test_contract_creation(self):
        contract = Contract(
            id="UK-POWER-MAR-2025",
            commodity=Commodity.POWER,
            delivery_period=DeliveryPeriod.MONTHLY,
            start_date=datetime(2025, 3, 1),
            end_date=datetime(2025, 3, 31),
            location="GB",
            tick_size=0.01,
            contract_size=1.0,
        )

        assert contract.id == "UK-POWER-MAR-2025"
        assert contract.commodity == "power"
        assert contract.delivery_period == "monthly"
        assert contract.start_date == datetime(2025, 3, 1)
        assert contract.end_date == datetime(2025, 3, 31)
        assert contract.location == "GB"
        assert contract.tick_size == 0.01
        assert contract.contract_size == 1.0
