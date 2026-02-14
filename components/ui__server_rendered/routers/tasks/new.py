from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_task_repository
from components.app__task.use_cases.create_task import create_task
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.tasks._helpers import create_from_form

router = APIRouter()


@router.get("/new")
def new_task_form(
    request: Request,
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="tasks/form.html",
        context={
            "request": request,
            "title": translate(lang, "tasks.form_new_title"),
            "mode": "create",
            "form_action": "/tasks/new",
            "values": {
                "office_id": "", "office_name": "", "type": "pickup", "status": "pending", "lat": "", "lng": "", "address": "", "time_window_start": "", "time_window_end": "", "service_duration_minutes": "0", "load_units": "0", "priority": "normal", "reference": "", "notes": ""
            },
            "errors": {},
            "lang": lang,
        },
    )


@router.post("/new")
async def create_task_ui(
    request: Request,
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    form_data = await request.form()
    payload, values, errors = create_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="tasks/form.html",
            context={"request": request, "title": translate(lang, "tasks.form_new_title"), "mode": "create", "form_action": "/tasks/new", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    create_task(repository=repository, **payload.model_dump())
    return RedirectResponse(url=f"/tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
