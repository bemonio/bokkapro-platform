from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from components.api__fastapi.dependencies import get_route_repository
from components.app__route.use_cases.delete_route import delete_route
from components.domain__route.errors import RouteNotFoundError
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale

router = APIRouter()


@router.post("/{route_uuid}/delete")
def delete_route_ui(route_uuid: str, repository: RouteRepositorySqlModel = Depends(get_route_repository), lang: str = Depends(get_locale)):
    try:
        delete_route(repository=repository, route_uuid=route_uuid)
    except RouteNotFoundError:
        raise HTTPException(status_code=404)
    return RedirectResponse(url=f"/routes?lang={lang}", status_code=303)
