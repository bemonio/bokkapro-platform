from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_task_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__task.use_cases.get_task import get_task
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{task_id}")
def view_task_ui(
    task_id: int,
    request: Request,
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    task = get_task(repository=repository, task_uuid=task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    office_options = [{"id": office.id, "name": office.name} for office in offices]
    return templates.TemplateResponse(
        request=request,
        name="tasks/form.html",
        context={
            "request": request,
            "title": translate(lang, "tasks.form_view_title", task_id=task_id),
            "mode": "view",
            "form_action": "",
            "values": {k: "" if getattr(task, k) is None else str(getattr(task, k)) for k in ["office_id", "type", "status", "lat", "lng", "address", "time_window_start", "time_window_end", "service_duration_minutes", "load_units", "priority", "reference", "notes"]},
            "errors": {},
            "office_options": office_options,
            "lang": lang,
        },
    )
