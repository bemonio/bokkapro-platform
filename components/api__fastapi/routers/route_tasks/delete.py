from fastapi import APIRouter, Depends, HTTPException, Response, status

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.delete_route_task import delete_route_task
from components.domain__route_task.errors import RouteTaskNotFoundError
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel

router = APIRouter()


@router.delete("/route-tasks/{route_task_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route_task_endpoint(route_task_uuid: str, repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository)) -> Response:
    try:
        delete_route_task(repository=repository, route_task_uuid=route_task_uuid)
    except RouteTaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
