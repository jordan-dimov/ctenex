from pydantic import Field, IPvAnyAddress

from ctenex.settings.base import CommonSettings


class APISettings(CommonSettings):
    api_host: IPvAnyAddress = Field(
        validation_alias="API_HOST",
        default=IPvAnyAddress("0.0.0.0"),  # type: ignore
    )
    api_port: int = Field(validation_alias="API_PORT", default=3000)
