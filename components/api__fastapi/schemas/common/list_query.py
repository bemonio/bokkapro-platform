from typing import Annotated, Literal

from fastapi import Query
from pydantic import BaseModel

OfficeSortField = Literal[
    "id",
    "name",
    "address",
    "lat",
    "lng",
    "storage_capacity",
    "created_at",
    "updated_at",
]
SortOrder = Literal["asc", "desc"]

DEFAULT_OFFICE_SORT: OfficeSortField = "name"
DEFAULT_OFFICE_ORDER: SortOrder = "asc"


class ListQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    search: str | None = None
    sort: OfficeSortField = DEFAULT_OFFICE_SORT
    order: SortOrder = DEFAULT_OFFICE_ORDER


def get_office_list_query_params(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query()] = None,
    sort: Annotated[OfficeSortField, Query()] = DEFAULT_OFFICE_SORT,
    order: Annotated[SortOrder, Query()] = DEFAULT_OFFICE_ORDER,
) -> ListQueryParams:
    normalized_search = " ".join(search.split()) if search is not None else None
    return ListQueryParams(
        page=page,
        page_size=page_size,
        search=normalized_search or None,
        sort=sort,
        order=order,
    )
