from typing import Annotated

from fastapi import APIRouter, Body, Request

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities import OpenOrderStatus
from ctenex.domain.order_book.order.model import Order
from ctenex.domain.order_book.order.schemas import OrderAddRequest, OrderAddResponse

router = APIRouter(tags=["exchange"])


@router.post("/orders")
def place_order(
    request: Request,
    body: Annotated[OrderAddRequest, Body()],
) -> OrderAddResponse:
    order = Order(**body.model_dump())

    order_id = request.app.state.matching_engine.add_order(order)
    return OrderAddResponse(
        **body.model_dump(),
        id=order_id,
        status=OpenOrderStatus.OPEN,
    )


@router.get("/orders")
def get_order(
    request: Request,
    contract_id: ContractCode,
) -> list[Order]:
    orders: list[Order] = request.app.state.matching_engine.get_orders(contract_id)
    return orders
