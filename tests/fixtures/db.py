import pytest_asyncio

from ctenex.core.db.async_session import (
    DatabaseManager,
    create_custom_engine,
    get_async_session,
)
from ctenex.settings.application import get_app_settings

db_settings = get_app_settings().db


@pytest_asyncio.fixture(scope="class")
async def async_session(session_generator=get_async_session):
    return session_generator


@pytest_asyncio.fixture(scope="class")
async def engine():
    engine = create_custom_engine(str(db_settings.uri))
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown_db(engine):
    await DatabaseManager.drop_db(engine=engine)
    await DatabaseManager.setup_db(engine=engine)
    yield
    await DatabaseManager.drop_db(engine=engine)
