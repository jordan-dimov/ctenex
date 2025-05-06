from enum import Enum
from typing import Literal

from pydantic import BaseModel

# Filtering

FilterType = str | int | bool


class BaseFilterParams(BaseModel):
    """
    Base class for filter parameters (this is the parameters container to be
    used in the query).

    When subclassing, define the filter parameters as fields.
    """

    def get_filters(self) -> dict[str, FilterType]:
        return self.model_dump(exclude_none=True, exclude_unset=True)


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
