import asyncio

from ctenex.core.db.async_session import DatabaseManager, create_custom_engine
from ctenex.domain.entities import Order  # noqa F401
from ctenex.settings.application import get_app_settings


async def init_db():
    db_settings = get_app_settings().db
    engine = create_custom_engine(str(db_settings.uri))

    await DatabaseManager.drop_db(engine=engine)
    await DatabaseManager.setup_db(engine=engine)


if __name__ == "__main__":
    asyncio.run(init_db())
