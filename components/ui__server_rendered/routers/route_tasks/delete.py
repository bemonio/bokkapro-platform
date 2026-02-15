from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.delete_route_task import delete_route_task
from components.domain__route_task.errors import RouteTaskNotFoundError
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale

router = APIRouter()


@router.post("/{route_task_uuid}/delete")
def delete_route_task_ui(
    route_task_uuid: str,
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
    lang: str = Depends(get_locale),
):
    try:
        delete_route_task(repository=repository, route_task_uuid=route_task_uuid)
    except RouteTaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(url=f"/route-tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
