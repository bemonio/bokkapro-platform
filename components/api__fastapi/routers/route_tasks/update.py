from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from components.api__fastapi.dependencies import get_route_task_repository
from components.api__fastapi.schemas.route_tasks.base import RouteTaskRead, RouteTaskUpdate
from components.app__route_task.use_cases.update_route_task import update_route_task
from components.domain__route_task.errors import RouteTaskNotFoundError
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel

router = APIRouter()


@router.put("/route-tasks/{route_task_uuid}", response_model=RouteTaskRead)
def update_route_task_endpoint(route_task_uuid: str, payload: RouteTaskUpdate, repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository)) -> RouteTaskRead:
    try:
        route_task = update_route_task(repository=repository, route_task_uuid=route_task_uuid, **payload.model_dump())
    except RouteTaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid route/task reference or duplicated sequence/task") from exc
    return RouteTaskRead.model_validate(route_task)
