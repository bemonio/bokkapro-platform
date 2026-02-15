from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_route_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_route_list_query_params
from components.app__route.use_cases.list_routes import list_routes
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.routes._helpers import build_pagination

router = APIRouter()


@router.get("")
@router.get("/")
def list_routes_ui(
    request: Request,
    params: ListQueryParams = Depends(get_route_list_query_params),
    repository: RouteRepositorySqlModel = Depends(get_route_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    items, total = list_routes(repository=repository, page=params.page, page_size=params.page_size, search=params.search, sort=params.sort, order=params.order)
    context = {
        "request": request,
        "title": translate(lang, "routes.title"),
        "routes": items,
        "search": params.search or "",
        "sort": params.sort,
        "order": params.order,
        "pagination": build_pagination(page=params.page, page_size=params.page_size, total=total),
        "lang": lang,
    }
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(request=request, name="routes/_table.html", context=context)
    return templates.TemplateResponse(request=request, name="routes/index.html", context=context)
