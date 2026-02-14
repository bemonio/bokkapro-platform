from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.entities import Vehicle
from components.domain__vehicle.errors import VehicleNotFoundError


def get_vehicle(repository: VehicleRepository, vehicle_uuid: str | int) -> Vehicle:
    vehicle = repository.get(vehicle_uuid) if isinstance(vehicle_uuid, int) else repository.get_by_uuid(vehicle_uuid)
    if vehicle is None:
        raise VehicleNotFoundError(f"Vehicle {vehicle_uuid} not found")
    return vehicle
