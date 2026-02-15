from fastapi import APIRouter, Depends, status

from components.api__fastapi.dependencies import get_route_repository
from components.api__fastapi.schemas.routes.base import RouteCreate, RouteRead
from components.app__route.use_cases.create_route import create_route
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel

router = APIRouter()


@router.post("/routes", response_model=RouteRead, status_code=status.HTTP_201_CREATED)
def create_route_endpoint(payload: RouteCreate, repository: RouteRepositorySqlModel = Depends(get_route_repository)) -> RouteRead:
    route = create_route(repository=repository, **payload.model_dump())
    return RouteRead.model_validate(route)
