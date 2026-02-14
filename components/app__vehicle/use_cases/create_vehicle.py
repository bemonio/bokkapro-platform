from uuid import uuid4

from bases.platform.time import utc_now
from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.entities import Vehicle


def create_vehicle(
    repository: VehicleRepository,
    *,
    office_id: int,
    name: str,
    plate: str | None,
    max_capacity: int,
    tenant_id: str | None = None,
    uuid: str | None = None,
) -> Vehicle:
    now = utc_now()
    vehicle = Vehicle(
        id=None,
        uuid=uuid or str(uuid4()),
        tenant_id=tenant_id,
        office_id=office_id,
        name=name,
        plate=plate,
        max_capacity=max_capacity,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    return repository.create(vehicle)
