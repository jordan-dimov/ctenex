import asyncio
from uuid import UUID

from loguru import logger

from ctenex.bot.exchange_bot import ExchangeBot
from ctenex.bot.orders_generators.alpha import AlphaOrdersGenerator
from ctenex.settings.application import get_app_settings

settings = get_app_settings()

BOT_TRADER_ID = UUID("135bb461-9b00-44eb-abe6-34a67ca9031e")


async def main():
    bot = ExchangeBot(
        trader_id=BOT_TRADER_ID,
        base_url=str(settings.api.base_url),
        contract_id="UK-BL-MAR-25",
        orders_generator=AlphaOrdersGenerator(),
    )
    try:
        await bot.validate_contract_id("UK-BL-MAR-25")
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
