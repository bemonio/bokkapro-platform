from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from components.api__fastapi.dependencies import get_task_repository
from components.app__task.use_cases.delete_task import delete_task
from components.domain__task.errors import TaskNotFoundError
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale

router = APIRouter()


@router.post("/{task_uuid}/delete")
def delete_task_ui(task_uuid: str, repository: TaskRepositorySqlModel = Depends(get_task_repository), lang: str = Depends(get_locale)):
    try:
        delete_task(repository=repository, task_uuid=task_uuid)
    except TaskNotFoundError:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=f"/tasks?lang={lang}", status_code=303)
