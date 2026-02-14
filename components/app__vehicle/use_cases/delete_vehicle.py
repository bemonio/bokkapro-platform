from bases.platform.time import utc_now
from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.errors import VehicleNotFoundError


def delete_vehicle(repository: VehicleRepository, vehicle_uuid: str | int) -> None:
    vehicle = repository.get(vehicle_uuid) if isinstance(vehicle_uuid, int) else repository.get_by_uuid(vehicle_uuid)
    if vehicle is None:
        raise VehicleNotFoundError(f"Vehicle {vehicle_uuid} not found")

    now = utc_now()
    vehicle.deleted_at = now
    vehicle.updated_at = now
    repository.soft_delete(vehicle)
