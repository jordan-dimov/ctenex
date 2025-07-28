from typing import Callable, Type, TypeAlias, get_args

from fastapi import Query

from ctenex.core.utils.filter_sort import SortOptions, SortOrder, SortParams


def parse_sorting(options: Type[SortOptions]) -> Callable:
    OptionsAlias: TypeAlias = options  # type: ignore[valid-type]

    async def _parse_sort(
        sort_by: OptionsAlias | None = Query(
            default=None,
            examples=None,
            description=f"A key to sort by. Options: {', '.join(options)}",
        ),
        sort_order: SortOrder | None = Query(
            default=None,
            description=f"Options: {', '.join(list(get_args(SortOrder)))}",
        ),
    ):
        if sort_by and sort_order:
            return SortParams(
                sort_by=sort_by,
                sort_order=sort_order,
            )

    return _parse_sort
