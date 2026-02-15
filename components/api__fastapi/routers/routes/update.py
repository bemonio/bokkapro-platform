from fastapi import APIRouter, Depends, HTTPException, status

from components.api__fastapi.dependencies import get_route_repository
from components.api__fastapi.schemas.routes.base import RouteRead, RouteUpdate
from components.app__route.use_cases.update_route import update_route
from components.domain__route.errors import RouteNotFoundError
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel

router = APIRouter()


@router.put("/routes/{route_uuid}", response_model=RouteRead)
def update_route_endpoint(route_uuid: str, payload: RouteUpdate, repository: RouteRepositorySqlModel = Depends(get_route_repository)) -> RouteRead:
    try:
        route = update_route(repository=repository, route_uuid=route_uuid, **payload.model_dump())
    except RouteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RouteRead.model_validate(route)
