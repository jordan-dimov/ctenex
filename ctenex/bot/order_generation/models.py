from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import OrderSide, OrderType


class OrderSpecification(BaseModel):
    """Represents a synthetic order."""

    id: UUID = Field(description="Order UUID")
    contract_id: ContractCode = Field(description="Contract identifier")
    trader_id: UUID = Field(description="Trader UUID")
    side: OrderSide = Field(description="Order side (buy/sell)")
    type: OrderType = Field(description="Order type (limit/market)")
    price: Decimal = Field(description="Order price")
    quantity: Decimal = Field(description="Order quantity")

    timestamp_reference: datetime = Field(
        default_factory=datetime.now,
        exclude=True,
        repr=False,
    )
    placed_at_absolute_timedelta_in_ms: int = Field(
        description="Time delta (in ms) from the reference time (absolute) to the order placement",
        exclude=True,
        repr=False,
    )

    @computed_field
    @property
    def placed_at(self) -> datetime:
        return self.timestamp_reference + timedelta(
            milliseconds=self.placed_at_absolute_timedelta_in_ms
        )


class Scenario(BaseModel):
    """
    Represents a test scenario. A scenario is a collection of orders and a description
    of what they represent or mean.
    """

    description: str = Field(description="Description of the test scenario")
    orders: list[OrderSpecification] = Field(description="List of orders")


class OrderGeneratorInput(BaseModel):
    """The input for the order generator."""

    scenario: Scenario
