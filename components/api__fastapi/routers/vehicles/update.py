from fastapi import APIRouter, Depends, HTTPException

from components.api__fastapi.dependencies import get_vehicle_repository
from components.api__fastapi.schemas.vehicles.base import VehicleRead, VehicleUpdate
from components.app__vehicle.use_cases.update_vehicle import update_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.put("/vehicles/{vehicle_uuid}", response_model=VehicleRead)
def update_vehicle_endpoint(
    vehicle_uuid: str,
    payload: VehicleUpdate,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
) -> VehicleRead:
    try:
        vehicle = update_vehicle(
            repository=repository,
            vehicle_uuid=vehicle_uuid,
            office_id=payload.office_id,
            name=payload.name,
            plate=payload.plate,
            max_capacity=payload.max_capacity,
        )
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return VehicleRead.model_validate(vehicle)
