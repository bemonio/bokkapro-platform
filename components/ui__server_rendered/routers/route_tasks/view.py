from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.get_route_task import get_route_task
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{route_task_uuid}")
def view_route_task_form(
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
        context={"request": request, "title": translate(lang, "route_tasks.form_view_title"), "mode": "view", "entity_uuid": route_task.uuid, "form_action": "#", "values": values, "errors": {}, "lang": lang},
    )
