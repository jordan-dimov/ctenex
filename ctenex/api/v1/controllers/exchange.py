from typing import Annotated

from fastapi import APIRouter, Body, Depends

from ctenex.core.db.async_session import AsyncSessionStream, db
from ctenex.core.db.utils import get_entity_values
from ctenex.domain.entities import OpenOrderStatus
from ctenex.domain.matching_engine.model import matching_engine
from ctenex.domain.order_book.contract.reader import contracts_reader
from ctenex.domain.order_book.contract.schemas import ContractGetResponse
from ctenex.domain.order_book.order.model import Order
from ctenex.domain.order_book.order.reader import OrderFilter
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderAddResponse,
    OrderGetResponse,
)

router = APIRouter(tags=["exchange"])


@router.post("/orders")
async def place_order(
    body: Annotated[OrderAddRequest, Body()],
) -> OrderAddResponse:
    order = Order(**body.model_dump())

    order_id = await matching_engine.add_order(order)
    return OrderAddResponse(
        **body.model_dump(),
        id=order_id,
        status=OpenOrderStatus.OPEN,
    )


@router.get("/orders")
async def get_orders(
    filter: Annotated[OrderFilter, Depends()],
    limit: int = 10,
    page: int = 1,
) -> list[OrderGetResponse]:
    orders: list[Order] = await matching_engine.get_orders(
        filter=filter,
        page=page,
        limit=limit,
    )
    return [OrderGetResponse(**order.model_dump(exclude_none=True)) for order in orders]


@router.get("/supported-contracts")
async def get_supported_contracts(
    limit: int = 10,
    page: int = 1,
    db: AsyncSessionStream = Depends(db),
) -> list[ContractGetResponse]:
    contracts = await contracts_reader.get_many(
        db=db,
        limit=limit,
        page=page,
    )
    return [
        ContractGetResponse(**get_entity_values(contract)) for contract in contracts
    ]
