import pathlib

from aiosqlite import connect


async def init_db(bot_name: str):
    """
    Initialize the bot database schema.

    This function will create the database file if it doesn't exist.
    It places the database file in the same directory as the script and
    names it after the bot name.

    It also assumes that the database schema is stored in the `sql` directory
    in a file named `init.sql`.
    """
    db_schema_path = pathlib.Path(__file__).parent / "sql" / "init.sql"
    db_path = pathlib.Path(__file__).parent / f"{bot_name}.db"

    init_script = db_schema_path.read_text()

    async with connect(db_path) as db:
        await db.executescript(init_script)
        await db.commit()
