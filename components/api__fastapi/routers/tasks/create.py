from fastapi import APIRouter, Depends, status

from components.api__fastapi.dependencies import get_task_repository
from components.api__fastapi.schemas.tasks.base import TaskCreate, TaskRead
from components.app__task.use_cases.create_task import create_task
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel

router = APIRouter()


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(payload: TaskCreate, repository: TaskRepositorySqlModel = Depends(get_task_repository)) -> TaskRead:
    task = create_task(repository=repository, **payload.model_dump())
    return TaskRead.model_validate(task)
