from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_task_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__task.use_cases.get_task import get_task
from components.app__task.use_cases.update_task import update_task
from components.domain__task.errors import TaskNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.tasks._helpers import update_from_form

router = APIRouter()


@router.get("/{task_uuid}/edit")
def edit_task_form(
    task_uuid: str,
    request: Request,
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    task = get_task(repository=repository, task_uuid=task_uuid)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    office_name = ""
    if task.office_id is not None:
        office = office_repository.get(task.office_id)
        if office is not None:
            office_name = office.name

    values = {k: "" if getattr(task, k) is None else str(getattr(task, k)) for k in ["office_id", "type", "status", "lat", "lng", "address", "time_window_start", "time_window_end", "service_duration_minutes", "load_units", "priority", "reference", "notes"]}
    values["office_name"] = office_name

    return templates.TemplateResponse(
        request=request,
        name="tasks/form.html",
        context={
            "request": request,
            "title": translate(lang, "tasks.form_edit_title"),
            "mode": "edit",
            "entity_uuid": task.uuid,
            "form_action": f"/tasks/{task.uuid}/edit",
            "values": values,
            "errors": {},
            "lang": lang,
        },
    )


@router.post("/{task_uuid}/edit")
async def edit_task_ui(
    task_uuid: str,
    request: Request,
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    office_options = [{"id": office.id, "name": office.name} for office in offices]
    task = get_task(repository=repository, task_uuid=task_uuid)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    form_data = await request.form()
    payload, values, errors = update_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="tasks/form.html",
            context={"request": request, "title": translate(lang, "tasks.form_edit_title"), "mode": "edit",
            "entity_uuid": task.uuid, "form_action": f"/tasks/{task.uuid}/edit", "values": values, "errors": errors, "office_options": office_options, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        update_task(repository=repository, task_uuid=task_uuid, **payload.model_dump())
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(url=f"/tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
