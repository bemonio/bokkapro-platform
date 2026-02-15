from fastapi import APIRouter, Depends, HTTPException, Response, status

from components.api__fastapi.dependencies import get_route_repository
from components.app__route.use_cases.delete_route import delete_route
from components.domain__route.errors import RouteNotFoundError
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel

router = APIRouter()


@router.delete("/routes/{route_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route_endpoint(route_uuid: str, repository: RouteRepositorySqlModel = Depends(get_route_repository)) -> Response:
    try:
        delete_route(repository=repository, route_uuid=route_uuid)
    except RouteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
