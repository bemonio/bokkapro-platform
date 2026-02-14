from fastapi import APIRouter, Depends, Request

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_office_list_query_params
from components.api__fastapi.schemas.common.pagination import Meta, PaginationMeta
from components.api__fastapi.schemas.offices.base import OfficeListResponse, OfficeRead
from components.app__office.use_cases.list_offices import list_offices
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.get("/offices", response_model=OfficeListResponse)
def list_offices_endpoint(
    request: Request,
    params: ListQueryParams = Depends(get_office_list_query_params),
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeListResponse:
    items, total = list_offices(
        repository=repository,
        page=params.page,
        page_size=params.page_size,
        search=params.search,
        sort=params.sort,
        order=params.order,
    )

    filters = {"search": params.search} if params.search else None
    sort = {"by": params.sort, "order": params.order} if "sort" in request.query_params or "order" in request.query_params else None

    return OfficeListResponse(
        data=[OfficeRead.model_validate(item) for item in items],
        meta=Meta(
            pagination=PaginationMeta.from_values(total=total, page=params.page, page_size=params.page_size),
            filters=filters,
            sort=sort,
        ),
    )
