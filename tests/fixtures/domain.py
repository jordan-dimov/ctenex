from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from ctenex.api.app_factory import create_app
from ctenex.api.controllers.status import router as status_router
from ctenex.api.v1.controllers.exchange import router as stateless_exchange_router
from ctenex.api.v1.in_memory.controllers.exchange import (
    router as stateful_exchange_router,
)
from ctenex.api.v1.in_memory.lifespan import lifespan
from ctenex.core.db.async_session import get_async_session
from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import (
    Commodity,
    Contract,
    Country,
    DeliveryPeriod,
    OrderSide,
    OrderType,
)
from ctenex.domain.order_book.order.model import Order


@pytest.fixture
def limit_buy_order():
    return Order(
        id=UUID("655889cb-b7c8-47f9-a302-cf9673f21445"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=UUID("a0130b4b-5f77-4703-9a18-1af5a87cc8eb"),
        side=OrderSide.BUY,
        type=OrderType.LIMIT,
        price=Decimal("100.0"),
        quantity=Decimal("10.0"),
        placed_at=datetime.now(UTC),
    )


@pytest.fixture
def limit_sell_order():
    return Order(
        id=UUID("7a89806f-4435-47b5-b475-ff535d1c4bc9"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=UUID("fe4f4479-6740-4103-9fb4-13f562b52b85"),
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        price=Decimal("100.0"),
        quantity=Decimal("10.0"),
        placed_at=datetime.now(UTC),
    )


@pytest.fixture
def second_limit_sell_order():
    return Order(
        id=UUID("7ec5a9b7-fc70-4056-802a-b466b5f6a162"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=UUID("fe4f4479-6740-4103-9fb4-13f562b52b85"),
        side=OrderSide.SELL,
        type=OrderType.LIMIT,
        price=Decimal("100.0"),
        quantity=Decimal("15.0"),
        placed_at=datetime.now(UTC),
    )


@pytest.fixture
def market_buy_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=uuid4(),
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        quantity=Decimal("10.0"),
        placed_at=datetime.now(UTC),
    )


@pytest.fixture
def second_market_buy_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=uuid4(),
        side=OrderSide.BUY,
        type=OrderType.MARKET,
        quantity=Decimal("15.0"),
        placed_at=datetime.now(UTC),
    )


@pytest.fixture
def market_sell_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id=uuid4(),
        side=OrderSide.SELL,
        type=OrderType.MARKET,
        quantity=Decimal("5.0"),
        placed_at=datetime.now(UTC),
    )


@pytest_asyncio.fixture
async def supported_contract_gb():
    async with get_async_session() as session:
        session.add(
            Country(
                country_id="GB",
                name="United Kingdom",
            )
        )
        await session.commit()

    supported_contract = Contract(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        commodity=Commodity.POWER,
        delivery_period=DeliveryPeriod.HOURLY,
        contract_size=Decimal("1.0"),
        location="GB",
        start_date=datetime(2025, 3, 1),
        end_date=datetime(2025, 3, 2),
        tick_size=Decimal("0.01"),
    )

    async with get_async_session() as session:
        session.add(supported_contract)
        await session.commit()
        await session.refresh(supported_contract)
    return supported_contract


# Route testing


@pytest.fixture
def client_for_stateful_app() -> Iterator[TestClient]:
    with TestClient(
        app=create_app(
            lifespan=lifespan,
            routers=[status_router, stateful_exchange_router],
        )
    ) as client:
        yield client


@pytest.fixture
def client_for_stateless_app() -> Iterator[TestClient]:
    with TestClient(
        app=create_app(
            routers=[status_router, stateless_exchange_router],
        )
    ) as client:
        yield client
