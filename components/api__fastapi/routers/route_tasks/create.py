from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from components.api__fastapi.dependencies import get_route_task_repository
from components.api__fastapi.schemas.route_tasks.base import RouteTaskCreate, RouteTaskRead
from components.app__route_task.use_cases.create_route_task import create_route_task
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel

router = APIRouter()


@router.post("/route-tasks", response_model=RouteTaskRead, status_code=status.HTTP_201_CREATED)
def create_route_task_endpoint(payload: RouteTaskCreate, repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository)) -> RouteTaskRead:
    try:
        route_task = create_route_task(repository=repository, **payload.model_dump())
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid route/task reference or duplicated sequence/task") from exc
    return RouteTaskRead.model_validate(route_task)
