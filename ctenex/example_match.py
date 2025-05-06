from decimal import Decimal
from uuid import UUID

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import OrderSide, OrderType
from ctenex.domain.in_memory.matching_engine.model import MatchingEngine
from ctenex.domain.order_book.order.model import Order


def example_match():
    matching_engine = MatchingEngine()
    matching_engine.start()

    # Add a limit buy order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("1e1590fd-f479-4bd4-ad03-56f2e265ec33"),
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            price=Decimal("100"),
            quantity=Decimal("100"),
        )
    )

    # Add a limit sell order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("71c2342f-e149-4b20-9e1f-b436072095b4"),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("101.50"),
            quantity=Decimal("100"),
        )
    )

    # Add a market buy order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("2f5ab7d8-7c60-4728-9410-1e5108382176"),
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity=Decimal("100"),
        )
    )

    # Add a limit sell order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id=UUID("391d8651-5ef8-4d17-9a0c-43c96c29b213"),
            side=OrderSide.SELL,
            type=OrderType.LIMIT,
            price=Decimal("99.50"),
            quantity=Decimal("100"),
        )
    )

    print(
        f"Total orders in {ContractCode.UK_BL_MAR_25} book: {len(matching_engine.get_orders(ContractCode.UK_BL_MAR_25))}"
    )


if __name__ == "__main__":
    example_match()
