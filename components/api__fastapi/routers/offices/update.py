from fastapi import APIRouter, Depends, HTTPException

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.offices.base import OfficeRead, OfficeUpdate
from components.app__office.use_cases.update_office import update_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.put("/offices/{office_uuid}", response_model=OfficeRead)
def update_office_endpoint(
    office_uuid: str,
    payload: OfficeUpdate,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeRead:
    try:
        office = update_office(
            repository=repository,
            office_uuid=office_uuid,
            name=payload.name,
            address=payload.address,
            place_id=payload.place_id,
            lat=payload.lat,
            lng=payload.lng,
            storage_capacity=payload.storage_capacity,
        )
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return OfficeRead.model_validate(office)
