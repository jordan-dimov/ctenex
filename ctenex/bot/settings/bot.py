from functools import lru_cache

from ctenex.bot.settings.base import CommonSettings
from ctenex.bot.settings.exchange_api import ExchangeAPISettings
from ctenex.bot.settings.sqlite import SqliteSettings


class BotSettings(CommonSettings):
    exchange_api: ExchangeAPISettings = ExchangeAPISettings()
    db: SqliteSettings = SqliteSettings()


@lru_cache(maxsize=1)
def get_bot_settings() -> BotSettings:
    return BotSettings()
