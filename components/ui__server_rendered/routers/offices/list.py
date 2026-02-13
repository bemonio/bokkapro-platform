from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.list_offices import list_offices
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_templates
from components.ui__server_rendered.routers.offices._helpers import build_pagination

router = APIRouter()


@router.get("")
@router.get("/")
def list_offices_ui(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    sort: Literal["name", "created_at", "updated_at"] = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    templates: Jinja2Templates = Depends(get_templates),
):
    items, total = list_offices(
        repository=repository,
        page=page,
        page_size=page_size,
        search=search,
        sort=sort,
        order=order,
    )
    context = {
        "request": request,
        "title": "Offices",
        "offices": items,
        "search": search or "",
        "sort": sort,
        "order": order,
        "pagination": build_pagination(page=page, page_size=page_size, total=total),
    }

    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(request=request, name="offices/_table.html", context=context)

    return templates.TemplateResponse(request=request, name="offices/index.html", context=context)
