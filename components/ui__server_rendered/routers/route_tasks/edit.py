from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.get_route_task import get_route_task
from components.app__route_task.use_cases.update_route_task import update_route_task
from components.domain__route_task.errors import RouteTaskNotFoundError
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.route_tasks._helpers import update_from_form

router = APIRouter()


@router.get("/{route_task_uuid}/edit")
def edit_route_task_form(
    route_task_uuid: str,
    request: Request,
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    route_task = get_route_task(repository=repository, route_task_uuid=route_task_uuid)
    if route_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    values = {k: "" if getattr(route_task, k) is None else str(getattr(route_task, k)) for k in ["route_uuid", "task_uuid", "sequence_order", "planned_arrival_at", "planned_departure_at", "actual_arrival_at", "actual_departure_at", "status"]}
    return templates.TemplateResponse(
        request=request,
        name="route_tasks/form.html",
        context={"request": request, "title": translate(lang, "route_tasks.form_edit_title"), "mode": "edit", "entity_uuid": route_task.uuid, "form_action": f"/route-tasks/{route_task.uuid}/edit", "values": values, "errors": {}, "lang": lang},
    )


@router.post("/{route_task_uuid}/edit")
async def edit_route_task_ui(
    route_task_uuid: str,
    request: Request,
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    route_task = get_route_task(repository=repository, route_task_uuid=route_task_uuid)
    if route_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    form_data = await request.form()
    payload, values, errors = update_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="route_tasks/form.html",
            context={"request": request, "title": translate(lang, "route_tasks.form_edit_title"), "mode": "edit", "entity_uuid": route_task.uuid, "form_action": f"/route-tasks/{route_task.uuid}/edit", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    try:
        update_route_task(repository=repository, route_task_uuid=route_task_uuid, **payload.model_dump())
    except RouteTaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        errors["__all__"] = translate(lang, "route_tasks.integrity_error")
        return templates.TemplateResponse(
            request=request,
            name="route_tasks/form.html",
            context={"request": request, "title": translate(lang, "route_tasks.form_edit_title"), "mode": "edit", "entity_uuid": route_task.uuid, "form_action": f"/route-tasks/{route_task.uuid}/edit", "values": values, "errors": errors, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse(url=f"/route-tasks?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
