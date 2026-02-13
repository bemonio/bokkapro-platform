from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.get_office import get_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_templates

router = APIRouter()


@router.get("/{office_id}")
def view_office(
    office_id: int,
    request: Request,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        office = get_office(repository=repository, office_id=office_id)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return templates.TemplateResponse(
        request=request,
        name="offices/form.html",
        context={
            "request": request,
            "title": f"Office #{office.id}",
            "mode": "view",
            "form_action": "#",
            "values": {
                "name": office.name,
                "address": office.address or "",
                "lat": "" if office.lat is None else str(office.lat),
                "lng": "" if office.lng is None else str(office.lng),
                "storage_capacity": str(office.storage_capacity),
            },
            "errors": {},
        },
    )
