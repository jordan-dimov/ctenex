from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from ctenex.domain.contracts import ContractCode
from ctenex.domain.order.model import OrderSide, OrderStatus, OrderType
from ctenex.domain.order.schemas import OrderAddRequest
from tests.fixtures import (
    client,  # noqa F401
    limit_buy_order,  # noqa F401
    limit_sell_order,  # noqa F401
    second_limit_sell_order,  # noqa F401
)


class TestExchangeRoute:
    def setup_method(self):
        self.url = "/orders"

    def test_add_limit_buy_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=10.0,
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
        assert payload["contract_id"] == order_request.contract_id
        assert payload["trader_id"] == order_request.trader_id
        assert payload["side"] == order_request.side
        assert payload["order_type"] == order_request.order_type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == order_request.quantity
        assert payload["status"] == OrderStatus.OPEN

    def test_add_limit_sell_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=10.0,
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
        assert payload["contract_id"] == order_request.contract_id
        assert payload["trader_id"] == order_request.trader_id
        assert payload["side"] == order_request.side
        assert payload["order_type"] == order_request.order_type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == order_request.quantity
        assert payload["status"] == OrderStatus.OPEN

    def test_add_market_buy_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10.0,
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
        assert payload["contract_id"] == order_request.contract_id
        assert payload["trader_id"] == order_request.trader_id
        assert payload["side"] == order_request.side
        assert payload["order_type"] == order_request.order_type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == order_request.quantity
        assert payload["status"] == OrderStatus.OPEN

    def test_add_market_sell_order(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=10.0,
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
        assert payload["contract_id"] == order_request.contract_id
        assert payload["trader_id"] == order_request.trader_id
        assert payload["side"] == order_request.side
        assert payload["order_type"] == order_request.order_type
        assert payload["price"] == order_request.price
        assert payload["quantity"] == order_request.quantity
        assert payload["status"] == OrderStatus.OPEN
