from fastapi import APIRouter, Depends, Request

from components.api__fastapi.dependencies import get_route_task_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_route_task_list_query_params
from components.api__fastapi.schemas.common.pagination import Meta, PaginationMeta
from components.api__fastapi.schemas.route_tasks.base import RouteTaskListResponse, RouteTaskRead
from components.app__route_task.use_cases.list_route_tasks import list_route_tasks
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel

router = APIRouter()


@router.get("/route-tasks", response_model=RouteTaskListResponse)
def list_route_tasks_endpoint(
    request: Request,
    params: ListQueryParams = Depends(get_route_task_list_query_params),
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
) -> RouteTaskListResponse:
    items, total = list_route_tasks(repository=repository, page=params.page, page_size=params.page_size, search=params.search, sort=params.sort, order=params.order)
    filters = {"search": params.search} if params.search else None
    sort = {"by": params.sort, "order": params.order} if "sort" in request.query_params or "order" in request.query_params else None
    return RouteTaskListResponse(
        data=[RouteTaskRead.model_validate(item) for item in items],
        meta=Meta(pagination=PaginationMeta.from_values(total=total, page=params.page, page_size=params.page_size), filters=filters, sort=sort),
    )
