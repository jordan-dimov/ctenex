from datetime import UTC, datetime
from typing import Iterator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from ctenex.api.app_factory import create_app
from ctenex.domain.contracts import ContractCode
from ctenex.domain.order.model import Order, OrderSide, OrderType


@pytest.fixture
def limit_buy_order():
    return Order(
        id=UUID("655889cb-b7c8-47f9-a302-cf9673f21445"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id="TRADER1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        price=100.0,
        quantity=10.0,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def limit_sell_order():
    return Order(
        id=UUID("7a89806f-4435-47b5-b475-ff535d1c4bc9"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id="TRADER2",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price=100.0,
        quantity=5.0,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def second_limit_sell_order():
    return Order(
        id=UUID("7ec5a9b7-fc70-4056-802a-b466b5f6a162"),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id="TRADER2",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price=100.0,
        quantity=15.0,
        created_at=datetime.now(UTC),
    )


# Route testing


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app=create_app()) as client:
        yield client
