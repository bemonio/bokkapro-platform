from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.create_route_task import create_route_task
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.route_tasks._helpers import create_from_form

router = APIRouter()


@router.get("/new")
def new_route_task_form(request: Request, lang: str = Depends(get_locale), templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(
        request=request,
        name="route_tasks/form.html",
        context={
            "request": request,
            "title": translate(lang, "route_tasks.form_new_title"),
            "mode": "create",
            "form_action": "/route-tasks/new",
            "values": {"route_uuid": "", "task_uuid": "", "sequence_order": "1", "planned_arrival_at": "", "planned_departure_at": "", "actual_arrival_at": "", "actual_departure_at": "", "status": "pending"},
            "errors": {},
            "lang": lang,
        },
    )


@router.post("/new")
async def create_route_task_ui(
    request: Request,
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    form_data = await request.form()
    payload, values, errors = create_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="route_tasks/form.html",
            context={"request": request, "title": translate(lang, "route_tasks.form_new_title"), "mode": "create", "form_action": "/route-tasks/new", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        create_route_task(repository=repository, **payload.model_dump())
    except IntegrityError:
        errors["__all__"] = translate(lang, "route_tasks.integrity_error")
        return templates.TemplateResponse(
            request=request,
            name="route_tasks/form.html",
            context={"request": request, "title": translate(lang, "route_tasks.form_new_title"), "mode": "create", "form_action": "/route-tasks/new", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse(url=f"/route-tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
