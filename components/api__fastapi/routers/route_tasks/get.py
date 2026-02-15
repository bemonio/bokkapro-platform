from fastapi import APIRouter, Depends, HTTPException, status

from components.api__fastapi.dependencies import get_route_task_repository
from components.api__fastapi.schemas.route_tasks.base import RouteTaskRead
from components.app__route_task.use_cases.get_route_task import get_route_task
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel

router = APIRouter()


@router.get("/route-tasks/{route_task_uuid}", response_model=RouteTaskRead)
def get_route_task_endpoint(route_task_uuid: str, repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository)) -> RouteTaskRead:
    route_task = get_route_task(repository=repository, route_task_uuid=route_task_uuid)
    if route_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route task not found")
    return RouteTaskRead.model_validate(route_task)
