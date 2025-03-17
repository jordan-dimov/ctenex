from datetime import UTC, datetime
from uuid import uuid4

import pytest

from ctenex.domain.contract_codes import ContractCode
from ctenex.domain.models.matching_engine import MatchingEngine
from ctenex.domain.models.order import Order, OrderSide, OrderStatus, OrderType


@pytest.fixture
def limit_buy_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.MAR_100_MW,
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
        id=uuid4(),
        contract_id=ContractCode.MAR_100_MW,
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
        id=uuid4(),
        contract_id=ContractCode.MAR_100_MW,
        trader_id="TRADER2",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price=100.0,
        quantity=15.0,
        created_at=datetime.now(UTC),
    )


class TestMatchingEngine:
    def setup_method(self):
        """Create a fresh matching engine before each test."""
        self.matching_engine = MatchingEngine()

    def test_add_limit_buy_order_no_match(self, limit_buy_order):
        """Test adding a limit buy order with no matching sells."""

        # Setup
        ...

        # Test
        trades = self.matching_engine.add_order(limit_buy_order)

        # Validation
        assert len(trades) == 0
        assert limit_buy_order.status == OrderStatus.OPEN
        assert limit_buy_order.remaining_quantity == limit_buy_order.quantity
        assert limit_buy_order in self.matching_engine.get_orders(
            ContractCode.MAR_100_MW
        )

    def test_add_limit_sell_order_no_match(self, limit_sell_order):
        """Test adding a limit sell order with no matching buys."""

        # Setup
        ...

        # Test
        trades = self.matching_engine.add_order(limit_sell_order)

        # Validation
        assert len(trades) == 0
        assert limit_sell_order.status == OrderStatus.OPEN
        assert limit_sell_order.remaining_quantity == limit_sell_order.quantity
        assert limit_sell_order in self.matching_engine.get_orders(
            ContractCode.MAR_100_MW
        )

    def test_match_limit_orders_exact_quantity(self, limit_buy_order, limit_sell_order):
        """Test matching limit orders with exact quantities."""

        # Setup
        limit_sell_order.quantity = limit_buy_order.quantity
        self.matching_engine.add_order(limit_buy_order)

        # Test
        trades = self.matching_engine.add_order(limit_sell_order)

        # Validation
        assert len(trades) == 1
        trade = trades[0]
        assert trade.buy_order_id == limit_buy_order.id
        assert trade.sell_order_id == limit_sell_order.id
        assert trade.quantity == limit_buy_order.quantity
        assert trade.price == limit_buy_order.price

        assert limit_buy_order.status == OrderStatus.FILLED
        assert limit_sell_order.status == OrderStatus.FILLED
        assert limit_buy_order.remaining_quantity == 0
        assert limit_sell_order.remaining_quantity == 0

        # Both orders should be removed from the book
        assert len(self.matching_engine.get_orders(ContractCode.MAR_100_MW)) == 0

    def test_match_limit_orders_with_partial_fill_of_buy_order(
        self, limit_buy_order, limit_sell_order
    ):
        """Test matching limit orders where one buy order is partially filled."""

        # Setup
        ...

        # Test
        self.matching_engine.add_order(limit_buy_order)  # Quantity: 10.0
        trades = self.matching_engine.add_order(limit_sell_order)  # Quantity: 5.0

        # Validation
        assert len(trades) == 1
        trade = trades[0]
        assert trade.quantity == 5.0

        assert limit_buy_order.status == OrderStatus.PARTIALLY_FILLED
        assert limit_sell_order.status == OrderStatus.FILLED
        assert limit_buy_order.remaining_quantity == 5.0
        assert limit_sell_order.remaining_quantity == 0

        # Buy order should remain in the book
        orders = self.matching_engine.get_orders(ContractCode.MAR_100_MW)
        assert len(orders) == 1
        assert limit_buy_order in orders

    def test_match_limit_orders_with_partial_fill_of_sell_order(
        self, limit_buy_order, second_limit_sell_order
    ):
        """Test matching limit orders where one sell order is partially filled."""

        # Setup
        ...

        # Test
        self.matching_engine.add_order(limit_buy_order)  # Quantity: 10.0
        trades = self.matching_engine.add_order(
            second_limit_sell_order
        )  # Quantity: 15.0

        # Validation
        assert len(trades) == 1
        trade = trades[0]
        assert trade.quantity == 10.0

        assert second_limit_sell_order.status == OrderStatus.PARTIALLY_FILLED
        assert limit_buy_order.status == OrderStatus.FILLED
        assert second_limit_sell_order.remaining_quantity == 5.0
        assert limit_buy_order.remaining_quantity == 0

        # Buy order should remain in the book
        orders = self.matching_engine.get_orders(ContractCode.MAR_100_MW)
        assert len(orders) == 1
        assert second_limit_sell_order in orders

    def test_match_market_buy_order(self, limit_sell_order):
        """Test matching a market buy order against existing sell orders."""

        # Setup
        self.matching_engine.add_order(limit_sell_order)
        market_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER3",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(market_order)

        # Validation
        assert len(trades) == 1
        trade = trades[0]
        assert trade.quantity == 5.0
        assert trade.price == limit_sell_order.price

        assert market_order.status == OrderStatus.FILLED
        assert limit_sell_order.status == OrderStatus.FILLED

        # Book should be empty
        assert len(self.matching_engine.get_orders(ContractCode.MAR_100_MW)) == 0

    def test_match_market_sell_order(self, limit_buy_order):
        """Test matching a market sell order against existing buy orders."""

        # Setup
        self.matching_engine.add_order(limit_buy_order)
        market_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER3",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(market_order)

        # Validation
        assert len(trades) == 1
        trade = trades[0]
        assert trade.quantity == 5.0
        assert trade.price == limit_buy_order.price

        assert market_order.status == OrderStatus.FILLED
        assert limit_buy_order.status == OrderStatus.PARTIALLY_FILLED
        assert limit_buy_order.remaining_quantity == 5.0

    def test_match_multiple_orders(self):
        """Test matching an order against multiple existing orders."""

        # Setup
        sell1 = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER1",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        sell2 = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=101.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        self.matching_engine.add_order(sell1)
        self.matching_engine.add_order(sell2)

        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER3",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=8.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(buy_order)

        # Validation
        assert len(trades) == 2
        assert trades[0].price == 100.0
        assert trades[0].quantity == 5.0
        assert trades[1].price == 101.0
        assert trades[1].quantity == 3.0

        assert sell1.status == OrderStatus.FILLED
        assert sell2.status == OrderStatus.PARTIALLY_FILLED
        assert buy_order.status == OrderStatus.FILLED
        assert sell2.remaining_quantity == 2.0

    def test_price_time_priority_matching(self):
        """Test orders are matched according to price-time priority."""

        # Setup
        sell1 = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER1",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        sell2 = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        self.matching_engine.add_order(sell1)  # First order at 100.0
        self.matching_engine.add_order(sell2)  # Second order at 100.0

        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER3",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=7.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(buy_order)

        # Validation
        assert len(trades) == 2
        # First trade should be with sell1 (first in time)
        assert trades[0].sell_order_id == sell1.id
        assert trades[0].quantity == 5.0
        # Second trade should be with sell2
        assert trades[1].sell_order_id == sell2.id
        assert trades[1].quantity == 2.0

    def test_get_trades(self, limit_buy_order, limit_sell_order):
        """Test retrieving trades for a specific contract."""

        # Setup
        self.matching_engine.add_order(limit_buy_order)
        self.matching_engine.add_order(limit_sell_order)

        # Test
        trades = self.matching_engine.get_trades(ContractCode.MAR_100_MW)

        # Validation
        assert len(trades) == 1
        assert all(t.contract_id == ContractCode.MAR_100_MW for t in trades)

    def test_limit_buy_order_respects_price_limit(self):
        """Test that a limit buy order does not match with asks above its limit price."""

        # Setup
        sell_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER1",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        self.matching_engine.add_order(sell_order)

        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER2",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=99.0,  # Lower than sell order price
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(buy_order)

        # Validation
        assert len(trades) == 0  # No trades should occur
        assert buy_order.status == OrderStatus.OPEN
        assert sell_order.status == OrderStatus.OPEN
        assert buy_order.remaining_quantity == 5.0
        assert sell_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = self.matching_engine.get_orders(ContractCode.MAR_100_MW)
        assert len(orders) == 2
        assert buy_order in orders
        assert sell_order in orders

    def test_limit_sell_order_respects_price_limit(self):
        """Test that a limit sell order does not match with bids below its limit price."""

        # Setup
        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )
        self.matching_engine.add_order(buy_order)

        sell_order = Order(
            id=uuid4(),
            contract_id=ContractCode.MAR_100_MW,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=101.0,  # Higher than buy order price
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        trades = self.matching_engine.add_order(sell_order)

        # Validation
        assert len(trades) == 0  # No trades should occur
        assert buy_order.status == OrderStatus.OPEN
        assert sell_order.status == OrderStatus.OPEN
        assert buy_order.remaining_quantity == 5.0
        assert sell_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = self.matching_engine.get_orders(ContractCode.MAR_100_MW)
        assert len(orders) == 2
        assert buy_order in orders
        assert sell_order in orders
