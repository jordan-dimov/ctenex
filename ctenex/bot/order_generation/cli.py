from ctenex.bot.order_generation.order_generator import OrderGenerator
from ctenex.bot.settings.bot import get_bot_settings
from ctenex.bot.utils.async_typer import AsyncTyper

settings = get_bot_settings()


app = AsyncTyper()


@app.command()
async def run_scenario(scenario_name: str):
    generator = OrderGenerator(
        scenario_name=scenario_name,
        base_url=str(settings.exchange_api.base_url),
    )

    generator.load_scenario()
    await generator.place_orders()


if __name__ == "__main__":
    app()
