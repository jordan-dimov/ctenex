import uuid
from typing import Protocol, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from ctenex.core.db.async_session import AsyncSessionStream
from ctenex.core.utils.filter_sort import BaseFilterParams, SortParams
from ctenex.domain.entities import AbstractBase

Entity = TypeVar("Entity", bound=AbstractBase)


class IRead(Protocol[Entity]):
    """Interface for operations that read from the database."""

    async def get(
        self,
        db: AsyncSessionStream,
        id: uuid.UUID,
    ) -> Entity | None:
        """Get an entity by its ID."""
        ...

    async def get_by(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams,
    ) -> Entity | None:
        """Get an entity using a key-value filter."""
        ...

    async def get_many(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> list[Entity]:
        """Get multiple entities using a filter, sort, limit, and page."""
        ...


class IWrite(Protocol[Entity]):
    """Interface for operations that change the state of the database."""

    async def create(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        """Create an entity."""
        ...

    async def update(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        """Update an entity."""
        ...

    async def delete(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        """Delete an entity."""
        ...


class Schema(BaseModel): ...
