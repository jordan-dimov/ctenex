from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import DECIMAL, TIMESTAMP, UUID, String

from ctenex.core.db.base import AbstractBase


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


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"


class OpenOrderStatus(str, Enum):
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"


class ProcessedOrderStatus(str, Enum):
    FILLED = "filled"
    CANCELLED = "cancelled"


OrderStatus = OpenOrderStatus | ProcessedOrderStatus


class BaseOrder(AbstractBase):
    """
    A generic model for orders. This is not a table in the database,
    but a base class for the 'Order', 'Bid', and 'Ask' classes.

    The 'status' column is meant to be implemented by the subclasses
    so they can set their own restrictions on the status.
    """

    __abstract__ = True

    contract_id: Mapped[str] = mapped_column(
        type_=String,
        nullable=False,
    )
    trader_id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        nullable=False,
    )
    side: Mapped[OrderSide] = mapped_column(
        type_=String,
        nullable=False,
    )
    type: Mapped[OrderType] = mapped_column(
        type_=String,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    placed_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
        index=True,
    )


class Contract(AbstractBase):
    __tablename__ = "contracts"
    __table_args__ = {"schema": "metadata"}

    contract_id: Mapped[str] = mapped_column(
        type_=String,
        unique=True,
    )
    commodity: Mapped[Commodity] = mapped_column(
        type_=String,
        nullable=False,
    )
    delivery_period: Mapped[DeliveryPeriod] = mapped_column(
        type_=String,
        nullable=False,
    )
    start_date: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=False,
    )
    tick_size: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    contract_size: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(ForeignKey("metadata.countries.country_id"))


class Country(AbstractBase):
    __tablename__ = "countries"
    __table_args__ = {"schema": "metadata"}

    country_id: Mapped[str] = mapped_column(
        type_=String,
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        type_=String,
        nullable=False,
    )


# Book aggregate


class Order(BaseOrder):
    __tablename__ = "orders"
    __table_args__ = {"schema": "book"}

    remaining_quantity: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        type_=String,
        nullable=False,
        default=OpenOrderStatus.OPEN,
    )


class BaseTrade(AbstractBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    contract_id: Mapped[str] = mapped_column(
        type_=String,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        type_=DECIMAL(precision=5, scale=2),
        nullable=False,
    )
    generated_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
    )


class Trade(BaseTrade):
    __tablename__ = "trades"
    __table_args__ = {"schema": "book"}

    buy_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.orders.id"))
    sell_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("book.orders.id"))

    bid = relationship(Order, foreign_keys=[buy_order_id])
    ask = relationship(Order, foreign_keys=[sell_order_id])


# History aggregate


class ProcessedOrder(BaseOrder):
    __abstract__ = True

    filled_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
        index=True,
    )
    status: Mapped[OrderStatus] = mapped_column(
        type_=String,
        nullable=False,
    )


class HistoricOrder(ProcessedOrder):
    __tablename__ = "historic_orders"
    __table_args__ = {"schema": "history"}


class HistoricTrade(BaseTrade):
    __tablename__ = "trades_history"
    __table_args__ = {"schema": "history"}

    buy_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("history.historic_orders.id")
    )
    sell_order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("history.historic_orders.id")
    )

    bid = relationship(HistoricOrder, foreign_keys=[buy_order_id])
    ask = relationship(HistoricOrder, foreign_keys=[sell_order_id])
