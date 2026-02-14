from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_task_repository
from components.app__office.use_cases.get_office import get_office
from components.app__task.use_cases.get_task import get_task
from components.app__task.use_cases.update_task import update_task
from components.domain__office.errors import OfficeNotFoundError
from components.domain__task.errors import TaskNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.tasks._helpers import update_from_form

router = APIRouter()


@router.get("/{task_id}/edit")
def edit_task_form(
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

    office_name = ""
    if task.office_id is not None:
        try:
            office = get_office(repository=office_repository, office_uuid=task.office_id)
            office_name = office.name
        except OfficeNotFoundError:
            office_name = ""

    values = {k: "" if getattr(task, k) is None else str(getattr(task, k)) for k in ["office_id", "type", "status", "lat", "lng", "address", "time_window_start", "time_window_end", "service_duration_minutes", "load_units", "priority", "reference", "notes"]}
    values["office_name"] = office_name

    return templates.TemplateResponse(
        request=request,
        name="tasks/form.html",
        context={
            "request": request,
            "title": translate(lang, "tasks.form_edit_title", task_id=task_id),
            "mode": "edit",
            "form_action": f"/tasks/{task_id}/edit",
            "values": values,
            "errors": {},
            "lang": lang,
        },
    )


@router.post("/{task_id}/edit")
async def edit_task_ui(
    task_id: int,
    request: Request,
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    form_data = await request.form()
    payload, values, errors = update_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="tasks/form.html",
            context={"request": request, "title": translate(lang, "tasks.form_edit_title", task_id=task_id), "mode": "edit", "form_action": f"/tasks/{task_id}/edit", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        update_task(repository=repository, task_uuid=task_id, **payload.model_dump())
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(url=f"/tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
