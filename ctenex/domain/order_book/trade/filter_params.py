from decimal import Decimal
from uuid import UUID

from ctenex.core.utils.filter_sort import BaseFilterParams


class TradeFilterParams(BaseFilterParams):
    """Filter parameters for orders."""

    contract_id: str | None = None
    price: Decimal | None = None
    quantity: Decimal | None = None
    buy_order_id: UUID | None = None
    sell_order_id: UUID | None = None
