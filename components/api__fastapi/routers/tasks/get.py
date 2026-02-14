from fastapi import APIRouter, Depends, HTTPException, status

from components.api__fastapi.dependencies import get_task_repository
from components.api__fastapi.schemas.tasks.base import TaskRead
from components.app__task.use_cases.get_task import get_task
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel

router = APIRouter()


@router.get("/tasks/{task_uuid}", response_model=TaskRead)
def get_task_endpoint(task_uuid: str, repository: TaskRepositorySqlModel = Depends(get_task_repository)) -> TaskRead:
    task = get_task(repository=repository, task_uuid=task_uuid)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskRead.model_validate(task)
