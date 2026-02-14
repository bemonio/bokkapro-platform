from fastapi import APIRouter, Depends, HTTPException

from components.api__fastapi.dependencies import get_vehicle_repository
from components.api__fastapi.schemas.vehicles.base import VehicleRead
from components.app__vehicle.use_cases.get_vehicle import get_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.get("/vehicles/{vehicle_uuid}", response_model=VehicleRead)
def get_vehicle_endpoint(
    vehicle_uuid: str,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
) -> VehicleRead:
    try:
        vehicle = get_vehicle(repository=repository, vehicle_uuid=vehicle_uuid)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return VehicleRead.model_validate(vehicle)
