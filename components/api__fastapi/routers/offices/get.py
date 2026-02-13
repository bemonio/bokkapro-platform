from fastapi import APIRouter, Depends, HTTPException

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.offices.base import OfficeRead
from components.app__office.use_cases.get_office import get_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.get("/offices/{office_id}", response_model=OfficeRead)
def get_office_endpoint(
    office_id: int,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeRead:
    try:
        office = get_office(repository=repository, office_id=office_id)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return OfficeRead.model_validate(office)
