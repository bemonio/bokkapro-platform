from fastapi import APIRouter, Depends, Request

from components.api__fastapi.dependencies import get_route_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_route_list_query_params
from components.api__fastapi.schemas.common.pagination import Meta, PaginationMeta
from components.api__fastapi.schemas.routes.base import RouteListResponse, RouteRead
from components.app__route.use_cases.list_routes import list_routes
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel

router = APIRouter()


@router.get("/routes", response_model=RouteListResponse)
def list_routes_endpoint(
    request: Request,
    params: ListQueryParams = Depends(get_route_list_query_params),
    repository: RouteRepositorySqlModel = Depends(get_route_repository),
) -> RouteListResponse:
    items, total = list_routes(repository=repository, page=params.page, page_size=params.page_size, search=params.search, sort=params.sort, order=params.order)
    filters = {"search": params.search} if params.search else None
    sort = {"by": params.sort, "order": params.order} if "sort" in request.query_params or "order" in request.query_params else None
    return RouteListResponse(
        data=[RouteRead.model_validate(item) for item in items],
        meta=Meta(pagination=PaginationMeta.from_values(total=total, page=params.page, page_size=params.page_size), filters=filters, sort=sort),
    )
