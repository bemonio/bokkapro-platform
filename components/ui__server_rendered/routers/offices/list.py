from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_office_list_query_params
from components.app__office.use_cases.list_offices import list_offices
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.offices._helpers import build_pagination

router = APIRouter()


@router.get("")
@router.get("/")
def list_offices_ui(
    request: Request,
    params: ListQueryParams = Depends(get_office_list_query_params),
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    items, total = list_offices(
        repository=repository,
        page=params.page,
        page_size=params.page_size,
        search=params.search,
        sort=params.sort,
        order=params.order,
    )
    context = {
        "request": request,
        "title": translate(lang, "offices.title"),
        "offices": items,
        "search": params.search or "",
        "sort": params.sort,
        "order": params.order,
        "pagination": build_pagination(page=params.page, page_size=params.page_size, total=total),
        "lang": lang,
    }

    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(request=request, name="offices/_table.html", context=context)

    return templates.TemplateResponse(request=request, name="offices/index.html", context=context)
