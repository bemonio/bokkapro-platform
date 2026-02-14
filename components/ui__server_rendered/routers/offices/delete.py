from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.delete_office import delete_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale

router = APIRouter()


@router.post("/{office_id}/delete")
def delete_office_ui(
    office_id: int,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
):
    try:
        delete_office(repository=repository, office_uuid=office_id)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RedirectResponse(url=f"/offices?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
