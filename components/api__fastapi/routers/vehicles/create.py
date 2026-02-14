from fastapi import APIRouter, Depends, status

from components.api__fastapi.dependencies import get_vehicle_repository
from components.api__fastapi.schemas.vehicles.base import VehicleCreate, VehicleRead
from components.app__vehicle.use_cases.create_vehicle import create_vehicle
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.post("/vehicles", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle_endpoint(
    payload: VehicleCreate,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
) -> VehicleRead:
    vehicle = create_vehicle(
        repository=repository,
        office_id=payload.office_id,
        name=payload.name,
        plate=payload.plate,
        lat=payload.lat,
        lng=payload.lng,
        max_capacity=payload.max_capacity,
    )
    return VehicleRead.model_validate(vehicle)
