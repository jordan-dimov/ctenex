from datetime import datetime, timezone
from pathlib import Path
from time import sleep

import httpx
import yaml
from loguru import logger

from ctenex.bot.order_generation.models import OrderGeneratorInput
from ctenex.domain.order_book.order.schemas import (
    OrderAddRequest,
    OrderAddResponse,
)

BASE_SCENARIO_PATH = Path(__file__).parent / "scenarios"


class OrderGenerator:
    def __init__(
        self,
        scenario_name: str,
        base_url: str,
    ):
        self.yaml_file_path = BASE_SCENARIO_PATH / f"{scenario_name}.yaml"
        self.exchange_client = httpx.AsyncClient(base_url=base_url)
        self.reference_time = datetime.now(timezone.utc)
        self.timestamps_deltas_in_ms: list[int] = []
        self.add_order_requests: list[OrderAddRequest] = []

    def load_scenario(self) -> None:
        """Load orders from YAML scenario file."""
        with open(self.yaml_file_path, "r") as file:
            data = yaml.safe_load(file)

        input_scenario = OrderGeneratorInput.model_validate(data)
        orders_data = input_scenario.scenario.orders

        for order in orders_data:
            self.timestamps_deltas_in_ms.append(
                order.placed_at_absolute_timedelta_in_ms
            )
            self.add_order_requests.append(OrderAddRequest(**order.model_dump()))

    async def place_order(self, order: OrderAddRequest) -> OrderAddResponse:
        response = await self.exchange_client.post(
            url="/v1/stateless/orders", json=order.model_dump(mode="json")
        )
        response.raise_for_status()

        logger.info(f"Placed order: {response.json()}")
        return OrderAddResponse(**response.json())

    async def place_orders(self) -> None:
        self.reference_time = datetime.now(timezone.utc)
        last_absolute_delta_in_ms = 0

        for time_delta_in_ms, add_request in zip(
            self.timestamps_deltas_in_ms, self.add_order_requests
        ):
            sleep((time_delta_in_ms - last_absolute_delta_in_ms) / 1000)
            await self.place_order(add_request)
            last_absolute_delta_in_ms = time_delta_in_ms
