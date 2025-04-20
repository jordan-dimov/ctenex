from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities.order.model import Order, OrderSide, OrderStatus, OrderType
from ctenex.domain.in_memory.order_book.model import OrderBook


@pytest.fixture
def order_book():
    return OrderBook(contract_id="TEST-CONTRACT")


@pytest.fixture
def sample_limit_buy_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id="TRADER1",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        price=100.0,
        quantity=10.0,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_limit_sell_order():
    return Order(
        id=uuid4(),
        contract_id=ContractCode.UK_BL_MAR_25,
        trader_id="TRADER2",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price=101.0,
        quantity=5.0,
        created_at=datetime.now(UTC),
    )


class TestOrderBook:
    def setup_method(self):
        self.order_book = OrderBook(contract_id=ContractCode.UK_BL_MAR_25)

    def test_add_limit_buy_order(self, sample_limit_buy_order):
        """Test adding a limit buy order to the book."""

        # Setup
        ...

        # Test
        order_id = self.order_book.add_order(sample_limit_buy_order)

        # Validation
        assert isinstance(order_id, UUID)
        assert self.order_book.orders_by_id[order_id] == sample_limit_buy_order
        assert sample_limit_buy_order in self.order_book.bid_queues[100.0]
        assert -100.0 in self.order_book.bids

    def test_add_limit_sell_order(self, sample_limit_sell_order):
        """Test adding a limit sell order to the book."""

        # Setup
        ...

        # Test
        order_id = self.order_book.add_order(sample_limit_sell_order)

        # Validation
        assert isinstance(order_id, UUID)
        assert sample_limit_sell_order in self.order_book.ask_queues[101.0]
        assert 101.0 in self.order_book.asks

    def test_add_market_buy_order(self):
        """Test adding a market buy order sets price to infinity."""

        # Setup
        market_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )

        # Test
        order_id = self.order_book.add_order(market_order)

        # Validation
        assert market_order.price == float("inf")
        assert self.order_book.orders_by_id[order_id] == market_order

    def test_add_market_sell_order(self):
        """Test adding a market sell order sets price to zero."""

        # Setup
        market_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.SELL,
            order_type=OrderType.MARKET,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )

        # Test
        order_id = self.order_book.add_order(market_order)

        # Validation
        assert market_order.price == 0.0
        assert self.order_book.orders_by_id[order_id] == market_order

    def test_add_limit_order_without_price_raises_error(self):
        """Test adding a limit order without price raises ValueError."""

        # Setup
        order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )

        # Test and validation
        with pytest.raises(ValueError, match="Order must have a price"):
            self.order_book.add_order(order)

    def test_cancel_existing_buy_order(self, sample_limit_buy_order):
        """Test cancelling an existing order."""

        # Setup
        order_id = self.order_book.add_order(sample_limit_buy_order)

        # Test
        cancelled_order = self.order_book.cancel_order(order_id)

        # Validation
        if cancelled_order:
            assert cancelled_order == sample_limit_buy_order
            assert cancelled_order.status == OrderStatus.CANCELLED
        assert order_id not in self.order_book.orders_by_id
        assert sample_limit_buy_order not in self.order_book.bid_queues[100.0]
        assert -100.0 not in self.order_book.bids

    def test_cancel_existing_sell_order(self, sample_limit_sell_order):
        """Test cancelling an existing order."""

        # Setup
        order_id = self.order_book.add_order(sample_limit_sell_order)

        # Test
        cancelled_order = self.order_book.cancel_order(order_id)

        # Validation
        if cancelled_order:
            assert cancelled_order == sample_limit_sell_order
            assert cancelled_order.status == OrderStatus.CANCELLED
        assert order_id not in self.order_book.orders_by_id
        assert sample_limit_sell_order not in self.order_book.ask_queues[101.0]
        assert 101.0 not in self.order_book.asks

    def test_cancel_nonexistent_order(self):
        """Test cancelling an order that doesn't exist returns None."""

        # Setup
        ...

        # Test
        result = self.order_book.cancel_order(uuid4())

        # Validation
        assert result is None

    def test_cancel_order_without_price_raises_error(self):
        """Test cancelling an order without price raises ValueError."""

        # Setup
        order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )
        self.order_book.orders_by_id[order.id] = order

        # Test and validation
        with pytest.raises(
            ValueError, match="Order cannot be cancelled as it has no price"
        ):
            self.order_book.cancel_order(order.id)

    def test_get_orders_returns_all_orders(
        self, sample_limit_buy_order, sample_limit_sell_order
    ):
        """Test get_orders returns all orders in the book."""

        # Setup
        ...

        # Test
        self.order_book.add_order(sample_limit_buy_order)
        self.order_book.add_order(sample_limit_sell_order)

        # Validation
        orders = self.order_book.get_orders()
        assert len(orders) == 2
        assert sample_limit_buy_order in orders
        assert sample_limit_sell_order in orders

    def test_get_orders_empty_book(self):
        """Test get_orders returns empty list for empty book."""

        # Setup
        ...

        # Test and validation
        assert self.order_book.get_orders() == []

    def test_price_time_priority_buy_orders(self):
        """Test buy orders are stored with price-time priority."""

        # Setup
        order1 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )
        order2 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER2",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=101.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)

        # Validation
        # Higher price should be first in bids
        assert list(self.order_book.bids.keys())[0] == -101.0

    def test_price_time_priority_sell_orders(self):
        """Test sell orders are stored with price-time priority."""

        # Setup
        order1 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER1",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=101.0,
            quantity=10.0,
            created_at=datetime.now(UTC),
        )
        order2 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="TRADER2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=100.0,
            quantity=5.0,
            created_at=datetime.now(UTC),
        )

        # Test
        self.order_book.add_order(order1)
        self.order_book.add_order(order2)

        # Validation
        # Lower price should be first in asks
        assert list(self.order_book.asks.keys())[0] == 100.0
