from datetime import UTC, datetime
from typing import Type

from loguru import logger
from sqlalchemy import column, inspect, update
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from ctenex.core.data_access.interfaces import Entity, IWrite


class GenericWriter(IWrite[Entity]):
    model: Type[Entity]

    async def create(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Creating a {self.model.__name__} record")

        session.add(entity)
        return entity

    async def update(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Updating a {self.model.__name__} record")
        await session.execute(
            update(self.model)
            .where(column("id") == entity.id)
            .values(
                **{
                    c.key: getattr(entity, c.key)
                    for c in inspect(entity).mapper.column_attrs
                }
            )
        )
        return entity

    async def delete(
        self,
        session: async_scoped_session[AsyncSession],
        entity: Entity,
    ) -> Entity:
        logger.info(f"Deleting a {self.model.__name__} record")

        # Soft delete
        entity.is_deleted = True
        entity.is_active = False
        entity.deleted_at = datetime.now(tz=UTC)

        session.add(entity)

        return entity
