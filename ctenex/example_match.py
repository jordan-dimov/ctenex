from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities.order.model import Order, OrderSide, OrderType
from ctenex.domain.in_memory.matching_engine.model import MatchingEngine


def example_match():
    matching_engine = MatchingEngine()

    # Add a limit buy order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="trader1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=100,
            quantity=100,
        )
    )

    # Add a limit sell order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="trader2",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=101.50,
            quantity=100,
        )
    )

    # Add a market buy order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="trader3",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
        )
    )

    # Add a limit sell order for contract MAR_100_MW
    matching_engine.add_order(
        Order(
            contract_id=ContractCode.UK_BL_MAR_25,
            trader_id="trader4",
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=99.50,
            quantity=100,
        )
    )

    print(
        f"Total orders in {ContractCode.UK_BL_MAR_25} book: {len(matching_engine.get_orders(ContractCode.UK_BL_MAR_25))}"
    )


if __name__ == "__main__":
    example_match()
