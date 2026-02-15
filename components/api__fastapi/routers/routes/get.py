from fastapi import APIRouter, Depends, HTTPException, status

from components.api__fastapi.dependencies import get_route_repository
from components.api__fastapi.schemas.routes.base import RouteRead
from components.app__route.use_cases.get_route import get_route
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel

router = APIRouter()


@router.get("/routes/{route_uuid}", response_model=RouteRead)
def get_route_endpoint(route_uuid: str, repository: RouteRepositorySqlModel = Depends(get_route_repository)) -> RouteRead:
    route = get_route(repository=repository, route_uuid=route_uuid)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return RouteRead.model_validate(route)
