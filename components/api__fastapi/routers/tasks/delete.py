from fastapi import APIRouter, Depends, HTTPException, Response, status

from components.api__fastapi.dependencies import get_task_repository
from components.app__task.use_cases.delete_task import delete_task
from components.domain__task.errors import TaskNotFoundError
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel

router = APIRouter()


@router.delete("/tasks/{task_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(task_uuid: str, repository: TaskRepositorySqlModel = Depends(get_task_repository)) -> Response:
    try:
        delete_task(repository=repository, task_uuid=task_uuid)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
