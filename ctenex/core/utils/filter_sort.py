from datetime import datetime
from enum import Enum
from typing import Literal, Type

from pydantic import BaseModel
from sqlalchemy import Select, column

from ctenex.core.db.base import AbstractBase
from ctenex.core.db.utils import get_entity_fields

# Filtering

# Timestamp-related filtering constants
TIMESTAMP_FIELD_SUFFIX = "_at"
TIMESTAMP_AT_OR_AFTER_FILTER_SUFFIX = "_at_or_after"
TIMESTAMP_BEFORE_FILTER_SUFFIX = "_before"


FilterType = str | int | bool | datetime


class BaseFilterParams(BaseModel):
    """
    Base class for filter parameters (this is the parameters container to be
    used in the query).

    When subclassing, define the filter parameters as fields.

    Note: datetime filters are only supported for datetime fields.

    When using datetime filters, the field name must end with `_or_after` and
    the name of the actual column must end with `_at`.
    The value must be a datetime object.

    Example for a model with a `placed_at` field:
    ```
    class OrderFilterParams(BaseFilterParams):
        contract_id: str | None = None
        placed_at_between: datetime | None = None
    ```
    """

    @property
    def total_number_of_filters(self) -> int:
        return len(self._get_filters())

    def _get_filters(self) -> dict[str, FilterType]:
        return self.model_dump(exclude_none=True, exclude_unset=True)

    def apply_to_statement(
        self,
        statement: Select,
        model: Type[AbstractBase],
    ) -> Select:
        filters = self._get_filters()

        table_column_names = get_entity_fields(model)

        # Get timestamp keys
        timestamp_column_names = [
            column_name
            for column_name in table_column_names
            if column_name.endswith(TIMESTAMP_FIELD_SUFFIX)
        ]

        timestamp_filters = {
            key: value
            for key, value in filters.items()
            if key.endswith(TIMESTAMP_AT_OR_AFTER_FILTER_SUFFIX)
            or key.endswith(TIMESTAMP_BEFORE_FILTER_SUFFIX)
        }

        # Check if any timestamp filter is valid (exists in table_column_names
        timestamp_column_names_from_valid_filters = {}

        for key in timestamp_filters.keys():
            if key.endswith(TIMESTAMP_AT_OR_AFTER_FILTER_SUFFIX):
                potentially_valid_timestamp_column_name = (
                    (key.split(TIMESTAMP_AT_OR_AFTER_FILTER_SUFFIX)[0])
                    + TIMESTAMP_FIELD_SUFFIX
                )
                if potentially_valid_timestamp_column_name in timestamp_column_names:
                    timestamp_column_names_from_valid_filters[key] = (
                        potentially_valid_timestamp_column_name
                    )
            elif key.endswith(TIMESTAMP_BEFORE_FILTER_SUFFIX):
                potentially_valid_timestamp_column_name = (
                    (key.split(TIMESTAMP_BEFORE_FILTER_SUFFIX)[0])
                    + TIMESTAMP_FIELD_SUFFIX
                )
                if potentially_valid_timestamp_column_name in timestamp_column_names:
                    timestamp_column_names_from_valid_filters[key] = (
                        potentially_valid_timestamp_column_name
                    )

        if len(timestamp_column_names_from_valid_filters) != len(timestamp_filters):
            raise ValueError(f"Invalid timestamp filters: {timestamp_filters}")

        # Apply filters
        for key, value in filters.items():
            if key.endswith(TIMESTAMP_BEFORE_FILTER_SUFFIX) and isinstance(
                value, datetime
            ):
                statement = statement.where(
                    column(timestamp_column_names_from_valid_filters[key]) < value
                )
            elif key.endswith(TIMESTAMP_AT_OR_AFTER_FILTER_SUFFIX) and isinstance(
                value, datetime
            ):
                statement = statement.where(
                    column(timestamp_column_names_from_valid_filters[key]) >= value
                )
            else:
                statement = statement.where(column(key) == value)
        return statement


# Sorting

SortOrder = Literal["asc", "desc"]


class SortParams(BaseModel):
    """
    Container class for the sorting parameters. To be populated with the
    `sort_by` and `sort_order` queries.
    """

    sort_by: str
    sort_order: SortOrder


class SortOptions(str, Enum):
    """When subclassing, define the available sorting options."""
