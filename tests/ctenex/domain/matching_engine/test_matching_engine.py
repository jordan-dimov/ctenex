from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import (
    OpenOrderStatus,
    OrderSide,
    OrderType,
    ProcessedOrderStatus,
)
from ctenex.domain.matching_engine.model import matching_engine
from ctenex.domain.order_book.order.model import Order
from ctenex.domain.order_book.order.reader import OrderFilter
from tests.fixtures.db import (
    async_session,  # noqa F811
    engine,  # noqa F811
    setup_and_teardown_db,  # noqa F811
)
from tests.fixtures.domain import (
    limit_buy_order,  # noqa F811
    limit_sell_order,  # noqa F811
    market_buy_order,  # noqa F811
    market_sell_order,  # noqa F811
    second_limit_sell_order,  # noqa F811
    second_market_buy_order,  # noqa F811
)


class TestMatchingEngine:
    def setup_method(self):
        """Create a fresh matching engine before each test."""
        self.matching_engine = matching_engine

    def teardown_method(self): ...

    async def test_add_limit_buy_order_no_match(
        self,
        limit_buy_order,  # noqa F811
    ):
        """Test adding a limit buy order with no matching sells."""

        # Setup
        ...

        # Test
        order_id = await self.matching_engine.add_order(limit_buy_order)

        # Validation
        assert limit_buy_order.id == order_id
        assert limit_buy_order.status == OpenOrderStatus.OPEN
        assert limit_buy_order.remaining_quantity == limit_buy_order.quantity
        assert limit_buy_order in await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )

    async def test_add_limit_sell_order_no_match(
        self,
        limit_sell_order,  # noqa F811
    ):
        """Test adding a limit sell order with no matching buys."""

        # Setup
        ...

        # Test
        order_id = await self.matching_engine.add_order(limit_sell_order)

        # Validation
        assert limit_sell_order.id == order_id
        assert limit_sell_order.status == OpenOrderStatus.OPEN
        assert limit_sell_order.remaining_quantity == limit_sell_order.quantity
        assert limit_sell_order in await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )

    async def test_match_limit_orders_exact_quantity(
        self,
        limit_buy_order,  # noqa F811
        limit_sell_order,  # noqa F811
    ):
        """Test matching limit orders with exact quantities."""

        # Setup
        limit_sell_order.quantity = limit_buy_order.quantity
        await self.matching_engine.add_order(limit_buy_order)

        # Test
        order_id = await self.matching_engine.add_order(limit_sell_order)

        # Validation
        assert limit_sell_order.id == order_id

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.id == limit_sell_order.id

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == ProcessedOrderStatus.FILLED
        assert filled_buy_order.id == limit_buy_order.id

    async def test_match_limit_orders_with_partial_fill_of_buy_order(
        self,
        limit_buy_order,  # noqa F811
        limit_sell_order,  # noqa F811
    ):
        """Test matching limit orders where one buy order is partially filled."""

        # Setup
        limit_sell_order.quantity = Decimal("5.0")

        # Test
        await self.matching_engine.add_order(limit_buy_order)  # Quantity: 10.0
        order_id = await self.matching_engine.add_order(
            limit_sell_order
        )  # Quantity: 5.0

        # Validation
        assert limit_sell_order.id == order_id

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.id == limit_sell_order.id
        assert filled_sell_order.remaining_quantity == 0

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == OpenOrderStatus.PARTIALLY_FILLED
        assert filled_buy_order.id == limit_buy_order.id
        assert filled_buy_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2

    async def test_match_limit_orders_with_partial_fill_of_sell_order(
        self,
        limit_buy_order,  # noqa F811
        second_limit_sell_order,  # noqa F811
    ):
        """Test matching limit orders where one sell order is partially filled."""

        # Setup
        ...

        # Test
        await self.matching_engine.add_order(limit_buy_order)  # Quantity: 10.0
        order_id = await self.matching_engine.add_order(
            second_limit_sell_order
        )  # Quantity: 15.0

        # Validation
        assert second_limit_sell_order.id == order_id

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            second_limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == OpenOrderStatus.PARTIALLY_FILLED
        assert filled_sell_order.remaining_quantity == 5.0

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == ProcessedOrderStatus.FILLED
        assert filled_buy_order.id == limit_buy_order.id
        assert filled_buy_order.remaining_quantity == 0

        # Both orders should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2

    async def test_match_market_buy_order(
        self,
        limit_sell_order,  # noqa F811
        market_buy_order,  # noqa F811
    ):
        """Test matching a market buy order against existing sell order."""

        # Setup
        await self.matching_engine.add_order(limit_sell_order)

        # Test
        order_id = await self.matching_engine.add_order(market_buy_order)

        # Validation
        assert market_buy_order.id == order_id

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            market_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == ProcessedOrderStatus.FILLED
        assert filled_buy_order.id == market_buy_order.id
        assert filled_buy_order.remaining_quantity == 0

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.id == limit_sell_order.id
        assert filled_sell_order.remaining_quantity == 0

        # Both should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2

    async def test_match_market_sell_order(
        self,
        limit_buy_order,  # noqa F811
        market_sell_order,  # noqa F811
    ):
        """Test matching a market sell order against existing buy orders."""

        # Setup
        await self.matching_engine.add_order(limit_buy_order)

        # Test
        order_id = await self.matching_engine.add_order(market_sell_order)

        # Validation
        assert market_sell_order.id == order_id

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            market_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.id == market_sell_order.id
        assert filled_sell_order.remaining_quantity == 0

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == OpenOrderStatus.PARTIALLY_FILLED
        assert filled_buy_order.id == limit_buy_order.id
        assert filled_buy_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2

    async def test_match_multiple_orders(
        self,
        limit_sell_order,  # noqa F811
        second_limit_sell_order,  # noqa F811
        second_market_buy_order,  # noqa F811
    ):
        """Test matching an order against multiple existing orders."""

        # Setup
        await self.matching_engine.add_order(limit_sell_order)
        await self.matching_engine.add_order(second_limit_sell_order)

        # Test
        order_id = await self.matching_engine.add_order(second_market_buy_order)

        # Validation
        assert second_market_buy_order.id == order_id

        # Full fill of buy order
        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            second_market_buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == ProcessedOrderStatus.FILLED
        assert filled_buy_order.id == second_market_buy_order.id
        assert filled_buy_order.remaining_quantity == 0

        # Full fill of sell order with quantity 5.0
        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.remaining_quantity == 0

        # Partial fill of sell order with quantity 15.0
        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            second_limit_sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == OpenOrderStatus.PARTIALLY_FILLED
        assert filled_sell_order.remaining_quantity == 10.0

    async def test_price_time_priority_matching(self):
        """Test orders are matched according to price-time priority."""

        # Setup
        sell1 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("100.0"),
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )
        sell2 = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("100.0"),
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )
        await self.matching_engine.add_order(sell1)  # First order at 100.0
        await self.matching_engine.add_order(sell2)  # Second order at 100.0

        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity=Decimal("7.0"),
            placed_at=datetime.now(UTC),
        )

        # Test
        order_id = await self.matching_engine.add_order(buy_order)

        # Validation
        assert buy_order.id == order_id

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == ProcessedOrderStatus.FILLED
        assert filled_buy_order.id == buy_order.id
        assert filled_buy_order.remaining_quantity == 0.0

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            sell1.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == ProcessedOrderStatus.FILLED
        assert filled_sell_order.id == sell1.id
        assert filled_sell_order.remaining_quantity == 0.0

    async def test_get_trades(
        self,
        limit_buy_order,  # noqa F811
        limit_sell_order,  # noqa F811
    ):
        """Test retrieving trades for a specific contract."""

        # Setup
        await self.matching_engine.add_order(limit_buy_order)
        await self.matching_engine.add_order(limit_sell_order)

        # Test
        trades = await self.matching_engine.get_trades_by_order(
            ContractCode.UK_BL_MAR_25,
            limit_buy_order.id,
        )

        # Validation
        assert trades is not None
        assert len(trades) == 1
        assert all(t.contract_id == ContractCode.UK_BL_MAR_25 for t in trades)

    async def test_limit_buy_order_respects_price_limit(self):
        """Test that a limit buy order does not match with asks above its limit price."""

        # Setup
        sell_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("100.0"),
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )
        await self.matching_engine.add_order(sell_order)

        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("99.0"),  # Lower than sell order price
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )

        # Test
        order_id = await self.matching_engine.add_order(buy_order)

        # Validation
        assert buy_order.id == order_id
        assert buy_order.status == OpenOrderStatus.OPEN
        assert sell_order.status == OpenOrderStatus.OPEN
        assert buy_order.remaining_quantity == 5.0
        assert sell_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == OpenOrderStatus.OPEN
        assert filled_buy_order.remaining_quantity == 5.0

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == OpenOrderStatus.OPEN
        assert filled_sell_order.remaining_quantity == 5.0

    async def test_limit_sell_order_respects_price_limit(self):
        """Test that a limit sell order does not match with bids below its limit price."""

        # Setup
        buy_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("100.0"),
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )
        await self.matching_engine.add_order(buy_order)

        sell_order = Order(
            id=uuid4(),
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=uuid4(),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("101.0"),  # Higher than buy order price
            quantity=Decimal("5.0"),
            placed_at=datetime.now(UTC),
        )

        # Test
        order_id = await self.matching_engine.add_order(sell_order)

        # Validation
        assert sell_order.id == order_id

        filled_buy_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            buy_order.id,
        )
        assert filled_buy_order is not None
        assert filled_buy_order.status == OpenOrderStatus.OPEN
        assert filled_buy_order.remaining_quantity == 5.0

        filled_sell_order = await self.matching_engine.get_order(
            ContractCode.UK_BL_MAR_25,
            sell_order.id,
        )
        assert filled_sell_order is not None
        assert filled_sell_order.status == OpenOrderStatus.OPEN
        assert filled_sell_order.remaining_quantity == 5.0

        # Both orders should remain in the book
        orders = await self.matching_engine.get_orders(
            filter=OrderFilter(
                contract_id=ContractCode.UK_BL_MAR_25,
            )
        )
        assert len(orders) == 2
