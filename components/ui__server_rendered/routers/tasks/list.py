from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_task_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_task_list_query_params
from components.app__task.use_cases.list_tasks import list_tasks
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.tasks._helpers import build_pagination

router = APIRouter()


@router.get("")
@router.get("/")
def list_tasks_ui(
    request: Request,
    params: ListQueryParams = Depends(get_task_list_query_params),
    repository: TaskRepositorySqlModel = Depends(get_task_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    items, total = list_tasks(repository=repository, page=params.page, page_size=params.page_size, search=params.search, sort=params.sort, order=params.order)
    context = {
        "request": request,
        "title": translate(lang, "tasks.title"),
        "tasks": items,
        "search": params.search or "",
        "sort": params.sort,
        "order": params.order,
        "pagination": build_pagination(page=params.page, page_size=params.page_size, total=total),
        "lang": lang,
    }
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(request=request, name="tasks/_table.html", context=context)
    return templates.TemplateResponse(request=request, name="tasks/index.html", context=context)
