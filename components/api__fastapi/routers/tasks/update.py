from fastapi import APIRouter, Depends, HTTPException, status

from components.api__fastapi.dependencies import get_task_repository
from components.api__fastapi.schemas.tasks.base import TaskRead, TaskUpdate
from components.app__task.use_cases.update_task import update_task
from components.domain__task.errors import TaskNotFoundError
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel

router = APIRouter()


@router.put("/tasks/{task_uuid}", response_model=TaskRead)
def update_task_endpoint(task_uuid: str, payload: TaskUpdate, repository: TaskRepositorySqlModel = Depends(get_task_repository)) -> TaskRead:
    try:
        task = update_task(repository=repository, task_uuid=task_uuid, **payload.model_dump())
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return TaskRead.model_validate(task)
