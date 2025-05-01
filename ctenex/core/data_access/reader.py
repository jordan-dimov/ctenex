import uuid
from typing import Type

from loguru import logger
from sqlalchemy import column, select

from ctenex.core.data_access.interfaces import Entity, IRead
from ctenex.core.db.async_session import AsyncSessionStream
from ctenex.core.utils.filter_sort import BaseFilterParams, SortParams
from ctenex.domain.exceptions import CoreException


class GenericReader(IRead[Entity]):
    model: Type[Entity]

    async def get(
        self,
        db: AsyncSessionStream,
        id: uuid.UUID,
    ) -> Entity | None:
        logger.info(f"Getting one {self.model.__name__} record by ID: {id}")

        statement = select(self.model).where(column("id") == id)

        async with db() as session:
            result = await session.scalar(statement)
            await session.commit()

        return result

    async def get_by(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams,
    ) -> Entity | None:
        """Read operation.

        Fetches a record by a filter key-value pair.
        """

        logger.info(f"Getting one {self.model.__name__} record by filter {filter}")

        filters = filter.get_filters()

        if len(filters) > 1:
            raise CoreException("Only one filter is allowed for this operation.")

        statement = select(self.model)

        for key, value in filters.items():
            statement = statement.where(column(key) == value)

        async with db() as session:
            result = await session.scalar(statement)
            await session.commit()

        return result

    async def get_many(
        self,
        db: AsyncSessionStream,
        filter: BaseFilterParams | None = None,
        sort: SortParams | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> list[Entity]:
        """Read operation.

        Fetches a list of records from the database with optional filtering,
         sorting and pagination.
        """

        logger.info(f"Getting several {self.model.__name__} records")

        statement = select(self.model)

        if filter:
            filters = filter.get_filters()

            for key, value in filters.items():
                statement = statement.where(column(key) == value)

        # Apply sorting
        if sort:
            statement = statement.order_by(
                column(sort.sort_by).asc()
                if sort.sort_order == "asc"
                else column(sort.sort_by).desc()
            )

        # Apply pagination
        page = 1 if page < 1 else page
        offset = (page - 1) * limit
        statement = statement.offset(offset).limit(limit)

        # Query
        logger.debug(statement.compile(compile_kwargs={"literal_binds": True}))

        async with db() as session:
            entities = await session.scalars(statement)
            await session.commit()
            result = list(entities.all())

        return result
