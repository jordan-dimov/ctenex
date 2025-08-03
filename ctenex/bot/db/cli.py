import pathlib
from typing import Literal

from aiosqlite import connect

from ctenex.bot.utils.async_typer import AsyncTyper


async def apply_schema_action(
    bot_name: str,
    up_or_down: Literal["up", "down"] = "up",
):
    """
    Apply a schema action. This function will create the database file if it doesn't exist.

    It places the database file in the same directory as the bot's implementation (under
    `ctenex/bot/bots/<bot_name>/`) and names it after the bot.

    It assumes that an action is a migration-like SQL file and exists in the `sql/schema/`
    subdirectory, inside the bot's implementation directory.

    The file should be named `up.sql` or `down.sql`.

    The `up.sql` file should contain the SQL statements to set up the schema.
    The `down.sql` file should contain the SQL statements to tear down the schema.
    """

    actions_path = (
        pathlib.Path(__file__).parent.parent
        / "bots"
        / bot_name
        / "sql"
        / "schema"
        / f"{up_or_down}.sql"
    )
    db_path = (
        pathlib.Path(__file__).parent.parent / "bots" / bot_name / f"{bot_name}_bot.db"
    )

    action_script = actions_path.read_text()

    async with connect(db_path) as db:
        await db.executescript(action_script)
        await db.commit()


app = AsyncTyper()


@app.command()
async def setup(bot_name: str):
    """Initialize the bot's database. This is a data-destructive operation."""
    await apply_schema_action(bot_name=bot_name, up_or_down="down")
    await apply_schema_action(bot_name=bot_name, up_or_down="up")


@app.command()
async def teardown(bot_name: str):
    """Teardown the bot's database. This is a data-destructive operation."""
    await apply_schema_action(bot_name=bot_name, up_or_down="down")


if __name__ == "__main__":
    app()
