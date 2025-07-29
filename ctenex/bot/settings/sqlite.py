from pathlib import Path

from pydantic import Field, computed_field

from ctenex.settings.base import CommonSettings

ROOT_DIR = Path(__file__).resolve().parent.parent


class SqliteSettings(CommonSettings):
    db: str | None = Field(validation_alias="BOT_DB_NAME", default="")

    @computed_field
    @property
    def db_path(self) -> str:
        return f"sqlite+aiosqlite:///{ROOT_DIR}/bots/{self.db}/{self.db}_bot.db"
