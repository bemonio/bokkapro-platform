from fastapi import APIRouter, Depends, status

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.offices.base import OfficeCreate, OfficeRead
from components.app__office.use_cases.create_office import create_office
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.post("/offices", response_model=OfficeRead, status_code=status.HTTP_201_CREATED)
def create_office_endpoint(
    payload: OfficeCreate,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeRead:
    office = create_office(
        repository=repository,
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        storage_capacity=payload.storage_capacity,
    )
    return OfficeRead.model_validate(office)
