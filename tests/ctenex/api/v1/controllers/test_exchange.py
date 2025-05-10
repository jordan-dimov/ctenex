from decimal import Decimal
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import (
    Commodity,
    DeliveryPeriod,
    OpenOrderStatus,
    OrderSide,
    OrderType,
    ProcessedOrderStatus,
)
from ctenex.domain.order_book.order.schemas import OrderAddRequest
from tests.fixtures.db import async_session, engine, setup_and_teardown_db  # noqa F401
from tests.fixtures.domain import client_for_stateless_app as client  # noqa F401
from tests.fixtures.domain import (
    limit_buy_order,  # noqa F401
    limit_sell_order,  # noqa F401
    second_limit_sell_order,  # noqa F401
    supported_contract_gb,  # noqa F401
)


class TestOrdersController:
    def setup_method(self):
        self.url = "/orders"

    # POST /orders

    def test_add_limit_buy_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("100.00"),
            quantity=Decimal("10.00"),
        )

        # test
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request),
        )

        # validation
        payload = response.json()

        assert response.status_code == 200

        assert isinstance(UUID(payload["id"]), UUID)
        assert payload["trader_id"] == str(order_request.trader_id)
        assert payload["contract_id"] == order_request.contract_id
        assert payload["side"] == order_request.side
        assert payload["type"] == order_request.type
        assert payload["price"] == str(order_request.price)
        assert payload["quantity"] == str(order_request.quantity)
        assert payload["status"] == OpenOrderStatus.OPEN

    def test_add_limit_sell_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("100.00"),
            quantity=Decimal("10.00"),
        )

        # test
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request),
        )

        # validation
        payload = response.json()

        assert response.status_code == 200

        assert isinstance(UUID(payload["id"]), UUID)
        assert payload["trader_id"] == str(order_request.trader_id)
        assert payload["contract_id"] == order_request.contract_id
        assert payload["side"] == order_request.side
        assert payload["type"] == order_request.type
        assert payload["price"] == str(order_request.price)
        assert payload["quantity"] == str(order_request.quantity)
        assert payload["status"] == OpenOrderStatus.OPEN

    def test_add_market_buy_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity=Decimal("10.00"),
        )

        # test
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request),
        )

        # validation
        payload = response.json()

        assert response.status_code == 200

        assert isinstance(UUID(payload["id"]), UUID)
        assert payload["trader_id"] == str(order_request.trader_id)
        assert payload["contract_id"] == order_request.contract_id
        assert payload["side"] == order_request.side
        assert payload["type"] == order_request.type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == str(order_request.quantity)
        assert payload["status"] == OpenOrderStatus.OPEN

    def test_add_market_sell_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.SELL,
            type=OrderType.MARKET,
            quantity=Decimal("10.00"),
        )

        # test
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request),
        )

        # validation
        payload = response.json()

        assert response.status_code == 200

        assert isinstance(UUID(payload["id"]), UUID)
        assert payload["trader_id"] == str(order_request.trader_id)
        assert payload["contract_id"] == order_request.contract_id
        assert payload["side"] == order_request.side
        assert payload["type"] == order_request.type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == str(order_request.quantity)
        assert payload["status"] == OpenOrderStatus.OPEN

    # GET /orders

    def test_get_orders(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request_1 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("100.00"),
            quantity=Decimal("10.00"),
        )
        order_request_2 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("101.00"),
            quantity=Decimal("10.00"),
        )
        order_request_3 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.SELL,
            type=OrderType.MARKET,
            quantity=Decimal("12.00"),
        )

        # test

        # 2 limit buy orders, with the second one having a higher price
        # therefore becoming the top of the book (best bid)
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request_1),
        )
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request_2),
        )

        # 1 market sell order, matched with the top of the book (best bid)
        # for 10 MW and with the second best bid for the remaining 2 MW
        response = client.post(
            url=self.url,
            json=jsonable_encoder(order_request_3),
        )

        response = client.get(
            url=self.url,
            params={"contract_id": "UK-BL-MAR-25"},
        )

        # validation
        payload = response.json()

        assert response.status_code == 200
        assert len(payload) == 3
        assert payload[0]["trader_id"] == str(order_request_1.trader_id)
        assert payload[0]["contract_id"] == order_request_1.contract_id
        assert payload[0]["side"] == order_request_1.side
        assert payload[0]["type"] == order_request_1.type
        assert payload[0]["price"] == str(order_request_1.price)
        assert payload[0]["quantity"] == str(order_request_1.quantity)
        assert payload[0]["status"] == ProcessedOrderStatus.FILLED

        assert payload[1]["trader_id"] == str(order_request_2.trader_id)
        assert payload[1]["contract_id"] == order_request_2.contract_id
        assert payload[1]["side"] == order_request_2.side
        assert payload[1]["type"] == order_request_2.type
        assert payload[1]["price"] == str(order_request_2.price)
        assert payload[1]["quantity"] == str(order_request_2.quantity)
        assert payload[1]["status"] == OpenOrderStatus.PARTIALLY_FILLED

        assert payload[2]["trader_id"] == str(order_request_3.trader_id)
        assert payload[2]["contract_id"] == order_request_3.contract_id
        assert payload[2]["side"] == order_request_3.side
        assert payload[2]["type"] == order_request_3.type
        assert payload[2]["quantity"] == str(order_request_3.quantity)
        assert payload[2]["status"] == ProcessedOrderStatus.FILLED


class TestContractsController:
    def setup_method(self):
        self.url = "/supported-contracts"

    async def test_get_supported_contracts_one_element(
        self,
        client: TestClient,  # noqa F811
        supported_contract_gb,  # noqa F811
    ):
        response = client.get(
            url=self.url,
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["contract_id"] == ContractCode.UK_BL_MAR_25
        assert response.json()[0]["commodity"] == Commodity.POWER
        assert response.json()[0]["delivery_period"] == DeliveryPeriod.HOURLY
        assert response.json()[0]["location"] == "GB"
        assert response.json()[0]["contract_size"] == "1.00"
        assert response.json()[0]["tick_size"] == "0.01"
        assert response.json()[0]["start_date"] == "2025-03-01T00:00:00Z"
        assert response.json()[0]["end_date"] == "2025-03-02T00:00:00Z"

    async def test_get_supported_contracts_empty(
        self,
        client: TestClient,  # noqa F811
    ):
        response = client.get(
            url=self.url,
        )

        assert response.status_code == 200
        assert len(response.json()) == 0
