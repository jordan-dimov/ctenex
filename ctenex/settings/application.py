from functools import lru_cache

from pydantic import Field

from ctenex.settings.api import APISettings
from ctenex.settings.base import CommonSettings
from ctenex.settings.postgres import PostgresSettings


class AppSettings(CommonSettings):
    api: APISettings = APISettings()
    db: PostgresSettings = PostgresSettings()

    environment: str = Field(validation_alias="ENVIRONMENT", default="dev")
    project_name: str = "CTENEX (Commodity Trading Exchange)"
    project_description: str = "A FastAPI-based API for commodity trading exchange."


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()
