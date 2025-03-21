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

    # GET /orders

    def test_get_orders(
        self,
        client: TestClient,  # noqa F811
    ):
        # setup
        order_request_1 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=10.0,
        )
        order_request_2 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER2",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=101.0,
            quantity=10.0,
        )
        order_request_3 = OrderAddRequest(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER3",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=12.0,
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
        assert len(payload) == 1
        assert payload[0]["contract_id"] == order_request_1.contract_id
        assert payload[0]["trader_id"] == order_request_1.trader_id
        assert payload[0]["side"] == order_request_1.side
        assert payload[0]["order_type"] == order_request_1.order_type
        assert payload[0]["price"] == order_request_1.price
        assert payload[0]["quantity"] == 10.0
        assert payload[0]["remaining_quantity"] == 8.0
        assert payload[0]["status"] == OrderStatus.PARTIALLY_FILLED
