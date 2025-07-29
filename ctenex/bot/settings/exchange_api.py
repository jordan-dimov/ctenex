from pydantic import Field, HttpUrl

from ctenex.settings.base import CommonSettings


class ExchangeAPISettings(CommonSettings):
    base_url: HttpUrl = Field(
        validation_alias="BOT_EXCHANGE_API_BASE_URL",
        default=HttpUrl("http://localhost:8000"),
    )
