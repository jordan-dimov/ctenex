import asyncio
from uuid import UUID

from loguru import logger

from ctenex.bot.bots.alpha.exchange_bot import ExchangeBot
from ctenex.bot.settings.bot import get_bot_settings

settings = get_bot_settings()

BOT_TRADER_ID = UUID("208384fa-4a29-46a4-a24b-8b11c8f278f3")


async def main():
    bot = ExchangeBot(
        trader_id=BOT_TRADER_ID,
        base_url=str(settings.exchange_api.base_url),
        contract_id="UK-BL-MAR-25",
    )
    try:
        await bot.validate_contract_id()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
