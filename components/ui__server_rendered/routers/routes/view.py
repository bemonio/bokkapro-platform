from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_route_repository
from components.app__route.use_cases.get_route import get_route
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{route_uuid}")
def view_route_ui(
    route_uuid: str,
    request: Request,
    repository: RouteRepositorySqlModel = Depends(get_route_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    route = get_route(repository=repository, route_uuid=route_uuid)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="routes/detail.html",
        context={
            "request": request,
            "title": translate(lang, "planning.route_detail_title"),
            "lang": lang,
            "route_uuid": route_uuid,
        },
    )
