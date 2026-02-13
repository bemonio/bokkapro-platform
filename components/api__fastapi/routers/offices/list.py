from typing import Literal

from fastapi import APIRouter, Depends, Query

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.offices.base import (
    ListMeta,
    OfficeListResponse,
    OfficeRead,
    PaginationMeta,
    SortMeta,
)
from components.api__fastapi.sorting import validate_sort_field
from components.app__office.use_cases.list_offices import list_offices
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()

OFFICE_ALLOWED_SORT_FIELDS = ("id", "name", "created_at", "updated_at")
DEFAULT_SORT_FIELD = "created_at"
DEFAULT_SORT_ORDER: Literal["asc", "desc"] = "desc"


@router.get("/offices", response_model=OfficeListResponse)
def list_offices_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    sort: str = Query(
        default=DEFAULT_SORT_FIELD,
        description="Sort field",
        json_schema_extra={"enum": list(OFFICE_ALLOWED_SORT_FIELDS)},
    ),
    order: Literal["asc", "desc"] = Query(default=DEFAULT_SORT_ORDER),
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeListResponse:
    sort = validate_sort_field(sort=sort, allowed_fields=OFFICE_ALLOWED_SORT_FIELDS)
    items, total = list_offices(
        repository=repository,
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
    )
    return OfficeListResponse(
        data=[OfficeRead.model_validate(item) for item in items],
        meta=ListMeta(
            pagination=PaginationMeta(page=page, page_size=page_size, total=total),
            filters={"search": search} if search else None,
            sort=SortMeta(field=sort, order=order),
        ),
    )
