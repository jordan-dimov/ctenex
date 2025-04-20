from typing import Annotated

from fastapi import APIRouter, Body, Request

from ctenex.domain.contracts import ContractCode
from ctenex.domain.entities.order.model import Order, OrderStatus
from ctenex.domain.entities.order.schemas import OrderAddRequest, OrderAddResponse

router = APIRouter(tags=["exchange"])


@router.post("/orders")
async def place_order(
    request: Request,
    body: Annotated[OrderAddRequest, Body()],
) -> OrderAddResponse:
    order = Order(**body.model_dump())

    order_id = request.app.state.matching_engine.add_order(order)
    return OrderAddResponse(
        **body.model_dump(),
        id=order_id,
        status=OrderStatus.OPEN,
    )


@router.get("/orders")
async def get_order(
    request: Request,
    contract_id: ContractCode,
) -> list[Order]:
    orders: list[Order] = request.app.state.matching_engine.get_orders(contract_id)
    return orders
