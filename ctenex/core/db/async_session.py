from __future__ import annotations

from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncIterator, Callable, Protocol

from sqlalchemy import DDL, Connection, Table, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    close_all_sessions,
    create_async_engine,
)

from ctenex.core.db.base import Base
from ctenex.settings.application import get_app_settings

db_settings = get_app_settings().db
env_settings = get_app_settings().environment


def create_custom_engine(uri: str) -> AsyncEngine:
    return create_async_engine(
        uri,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=0,
        pool_recycle=25,
        echo=env_settings == "dev",
    )


class DatabaseManager:
    @staticmethod
    @event.listens_for(Table, "before_create")
    def create_schema_if_not_exists(target: Table, connection: Connection, **_):
        connection.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {target.schema}"))

    @staticmethod
    async def setup_db(engine: AsyncEngine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_db(engine: AsyncEngine):
        await close_all_sessions()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


class AsyncDatabaseConnection:
    """
    A synchronous database connection manager that provides
    SQLAlchemy scoped session objects. Sessions are thread-local
    scoped by default.
    """

    def __init__(
        self,
        engine: AsyncEngine,
    ) -> None:
        self._engine: AsyncEngine = engine
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def get_engine(self) -> AsyncEngine:
        if not self._engine:
            self._engine = create_custom_engine(str(db_settings.uri))
        return self._engine

    async def close_engine(self) -> None:
        if self._engine:
            await self._engine.dispose()

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        if not self._session_factory:
            self._session_factory = async_sessionmaker(
                bind=self.get_engine(),
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory

    def get_session(
        self,
        current_scope: Callable = current_task,
    ) -> async_scoped_session[AsyncSession]:
        """
        Returns a scoped session object. The `scopefunc` argument is set to the
        current thread by default. This can be overridden by passing a callable
        that returns a unique identifier (for instance, for the current request or task).
        """
        return async_scoped_session(self.get_session_factory(), scopefunc=current_scope)

    async def test_connection(self) -> bool:
        try:
            async with self.get_engine().begin() as conn:
                await conn.execute(text("SELECT 1"))
                return True
        except SQLAlchemyError:
            return False


db_connection = AsyncDatabaseConnection(
    engine=create_custom_engine(str(db_settings.uri))
)


class AsyncSessionProvider(Protocol):
    """Protocol for async session providers."""

    def get_session(
        self,
        current_scope: Callable,
    ) -> async_scoped_session[AsyncSession]: ...

    async def close_engine(self) -> None: ...


class AsyncSessionStream(Protocol):
    """Protocol for the get_async_session context manager."""

    def __call__(
        self,
        connection: AsyncDatabaseConnection = db_connection,
        current_scope: Callable = current_task,
    ) -> AsyncContextManager[async_scoped_session[AsyncSession]]: ...


@asynccontextmanager
async def get_async_session(
    connection: AsyncDatabaseConnection = db_connection,
    current_scope: Callable = current_task,
) -> AsyncIterator[async_scoped_session[AsyncSession]]:
    session: async_scoped_session[AsyncSession] | None = None

    try:
        session = connection.get_session(current_scope=current_scope)
        yield session
    except SQLAlchemyError:
        if session is not None:
            await session.rollback()
        raise
    finally:
        if session is not None:
            await session.close()
            await connection.close_engine()


class AsyncSessionStreamProvider:
    def __init__(self):
        self.session_stream: AsyncSessionStream = get_async_session

    def __call__(self):
        return self.session_stream


db = AsyncSessionStreamProvider()
