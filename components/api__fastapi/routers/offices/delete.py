from fastapi import APIRouter, Depends, HTTPException, Response, status

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.delete_office import delete_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.delete("/offices/{office_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_office_endpoint(
    office_uuid: str,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> Response:
    try:
        delete_office(repository=repository, office_uuid=office_uuid)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
