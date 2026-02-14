from fastapi import APIRouter, Depends, Request

from components.api__fastapi.dependencies import get_task_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_task_list_query_params
from components.api__fastapi.schemas.common.pagination import Meta, PaginationMeta
from components.api__fastapi.schemas.tasks.base import TaskListResponse, TaskRead
from components.app__task.use_cases.list_tasks import list_tasks
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel

router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
def list_tasks_endpoint(
    request: Request,
    params: ListQueryParams = Depends(get_task_list_query_params),
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
) -> TaskListResponse:
    items, total = list_tasks(repository=repository, page=params.page, page_size=params.page_size, search=params.search, sort=params.sort, order=params.order)
    filters = {"search": params.search} if params.search else None
    sort = {"by": params.sort, "order": params.order} if "sort" in request.query_params or "order" in request.query_params else None
    return TaskListResponse(
        data=[TaskRead.model_validate(item) for item in items],
        meta=Meta(pagination=PaginationMeta.from_values(total=total, page=params.page, page_size=params.page_size), filters=filters, sort=sort),
    )
