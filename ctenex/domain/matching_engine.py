from typing import Type
from uuid import UUID

from loguru import logger

from ctenex.domain.contracts import ContractCode
from ctenex.domain.order.model import Order, OrderSide, OrderStatus, OrderType
from ctenex.domain.order_book import OrderBook
from ctenex.domain.trade.model import Trade


class MatchingEngine:
    def __init__(self):
        self.order_books: dict[ContractCode, OrderBook] = {}
        self.trades: list[Trade] = []

    def start(self, contract_codes: Type[ContractCode] = ContractCode):
        """Start the matching engine and create order books for all contract codes."""
        for contract_code in contract_codes:
            self.order_books[contract_code] = OrderBook(contract_code)

    def stop(self):
        """Stop the matching engine and clear all order books."""
        self.order_books.clear()

    def add_order(self, order: Order) -> UUID:
        """Add an order to the book and return any trades that result."""
        logger.debug(f"Adding order: {order}")

        if order.remaining_quantity is None:
            order.remaining_quantity = order.quantity

        # Try to match the order first
        if order.side == OrderSide.BUY:
            trades = self._match_buy_order(order)
        else:
            trades = self._match_sell_order(order)

        # If order still has quantity remaining, add to book
        # (only for limit orders) <- TODO: review this
        if order.remaining_quantity > 0 and order.order_type == OrderType.LIMIT:
            self.order_books[order.contract_id].add_order(order)

        self.trades.extend(trades)

        return order.id

    def get_orders(self, contract_id: ContractCode) -> list[Order]:
        return self.order_books[contract_id].get_orders()

    def get_trades(self, contract_id: ContractCode) -> list[Trade]:
        return [trade for trade in self.trades if trade.contract_id == contract_id]

    def _match_buy_order(self, buy_order: Order) -> list[Trade]:
        trades = []
        order_book = self.order_books[buy_order.contract_id]

        while buy_order.remaining_quantity and buy_order.remaining_quantity > 0:
            # Check if there are any asks to match against
            if not order_book.asks or not order_book.ask_queues:
                break

            best_ask_price = order_book.asks.keys()[0]

            # For limit orders, check if the price is acceptable
            if (
                buy_order.order_type == OrderType.LIMIT
                and best_ask_price > buy_order.price
            ):
                break

            # Match against the best ask price
            ask_queue = order_book.ask_queues[best_ask_price]
            while ask_queue and buy_order.remaining_quantity > 0:
                sell_order = ask_queue[0]

                # Calculate trade quantity
                trade_quantity = min(
                    buy_order.remaining_quantity, sell_order.remaining_quantity
                )

                # Create and record the trade
                trade = Trade(
                    contract_id=order_book.contract_id,
                    buy_order_id=buy_order.id,
                    sell_order_id=sell_order.id,
                    price=best_ask_price,
                    quantity=trade_quantity,
                )
                trades.append(trade)

                # Update order quantities
                buy_order.remaining_quantity -= trade_quantity
                sell_order.remaining_quantity -= trade_quantity

                # Update order statuses
                if sell_order.remaining_quantity == 0:
                    sell_order.status = OrderStatus.FILLED
                    ask_queue.pop(0)
                    order_book.orders_by_id.pop(sell_order.id)
                else:
                    sell_order.status = OrderStatus.PARTIALLY_FILLED

                if buy_order.remaining_quantity == 0:
                    buy_order.status = OrderStatus.FILLED
                else:
                    buy_order.status = OrderStatus.PARTIALLY_FILLED

            # If ask queue is empty, remove the price level
            if not ask_queue:
                order_book.ask_queues.pop(best_ask_price)
                order_book.asks.pop(best_ask_price)

        if len(trades) > 0:
            logger.debug(f"Matched order with ID {buy_order.id}")
            logger.debug(f"Generated {len(trades)} trades:")
            for trade in trades:
                logger.debug(trade)

        return trades

    def _match_sell_order(self, sell_order: Order) -> list[Trade]:
        trades = []
        order_book = self.order_books[sell_order.contract_id]

        while sell_order.remaining_quantity and sell_order.remaining_quantity > 0:
            # Check if there are any bids to match against
            if not order_book.bids or not order_book.bid_queues:
                break

            best_bid_price = -order_book.bids.keys()[0]  # Convert back from negative

            # For limit orders, check if the price is acceptable
            if (
                sell_order.order_type == OrderType.LIMIT
                and best_bid_price < sell_order.price
            ):
                break

            # Match against the best bid price
            bid_queue = order_book.bid_queues[best_bid_price]
            while bid_queue and sell_order.remaining_quantity > 0:
                buy_order = bid_queue[0]

                # Calculate trade quantity
                trade_quantity = min(
                    sell_order.remaining_quantity, buy_order.remaining_quantity
                )

                # Create and record the trade
                trade = Trade(
                    contract_id=sell_order.contract_id,
                    buy_order_id=buy_order.id,
                    sell_order_id=sell_order.id,
                    price=best_bid_price,
                    quantity=trade_quantity,
                )
                trades.append(trade)

                # Update order quantities
                sell_order.remaining_quantity -= trade_quantity
                buy_order.remaining_quantity -= trade_quantity

                # Update order statuses
                if buy_order.remaining_quantity == 0:
                    buy_order.status = OrderStatus.FILLED
                    bid_queue.pop(0)
                    order_book.orders_by_id.pop(buy_order.id)
                else:
                    buy_order.status = OrderStatus.PARTIALLY_FILLED

                if sell_order.remaining_quantity == 0:
                    sell_order.status = OrderStatus.FILLED
                else:
                    sell_order.status = OrderStatus.PARTIALLY_FILLED

            # If bid queue is empty, remove the price level
            if not bid_queue:
                order_book.bid_queues.pop(best_bid_price)
                order_book.bids.pop(-best_bid_price)

        # Temp
        if len(trades) > 0:
            logger.debug(f"Matched order with ID {sell_order.id}")
            logger.debug(f"Generated {len(trades)} trades:")
            for trade in trades:
                logger.debug(trade)

        return trades
