from fastapi import APIRouter, Depends, HTTPException, Response, status

from components.api__fastapi.dependencies import get_vehicle_repository
from components.app__vehicle.use_cases.delete_vehicle import delete_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.delete("/vehicles/{vehicle_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_endpoint(
    vehicle_uuid: str,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
) -> Response:
    try:
        delete_vehicle(repository=repository, vehicle_uuid=vehicle_uuid)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
