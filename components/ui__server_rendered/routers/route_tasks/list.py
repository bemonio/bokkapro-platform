from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_route_task_repository
from components.app__route_task.use_cases.list_route_tasks import list_route_tasks
from components.persistence__sqlmodel.repositories.route_tasks_repo import RouteTaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.route_tasks._helpers import build_pagination

router = APIRouter()


@router.get("")
def list_route_tasks_ui(
    request: Request,
    repository: RouteTaskRepositorySqlModel = Depends(get_route_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    page = max(int(request.query_params.get("page", 1)), 1)
    page_size = max(min(int(request.query_params.get("page_size", 20)), 100), 1)
    search = request.query_params.get("search")
    sort = request.query_params.get("sort", "sequence_order")
    order = request.query_params.get("order", "asc")

    items, total = list_route_tasks(repository=repository, page=page, page_size=page_size, search=search, sort=sort, order=order)
    pagination = build_pagination(total=total, page=page, page_size=page_size)
    context = {
        "request": request,
        "title": translate(lang, "route_tasks.title"),
        "route_tasks": items,
        "pagination": pagination,
        "search": search or "",
        "sort": sort,
        "order": order,
        "lang": lang,
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse(request=request, name="route_tasks/_table.html", context=context)
    return templates.TemplateResponse(request=request, name="route_tasks/index.html", context=context)
