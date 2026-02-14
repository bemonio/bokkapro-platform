from bases.platform.time import utc_now
from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.entities import Vehicle
from components.domain__vehicle.errors import VehicleNotFoundError


def update_vehicle(
    repository: VehicleRepository,
    vehicle_uuid: str | int,
    *,
    office_id: int | None = None,
    name: str | None = None,
    plate: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    max_capacity: int | None = None,
) -> Vehicle:
    vehicle = repository.get(vehicle_uuid) if isinstance(vehicle_uuid, int) else repository.get_by_uuid(vehicle_uuid)
    if vehicle is None:
        raise VehicleNotFoundError(f"Vehicle {vehicle_uuid} not found")

    if office_id is not None:
        vehicle.office_id = office_id
    if name is not None:
        vehicle.name = name
    if plate is not None:
        vehicle.plate = plate
    if lat is not None:
        vehicle.lat = lat
    if lng is not None:
        vehicle.lng = lng
    if max_capacity is not None:
        vehicle.max_capacity = max_capacity

    vehicle.updated_at = utc_now()
    return repository.update(vehicle)
