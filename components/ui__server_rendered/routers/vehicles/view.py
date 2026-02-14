from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_vehicle_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__vehicle.use_cases.get_vehicle import get_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{vehicle_id}")
def view_vehicle(
    vehicle_id: int,
    request: Request,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        vehicle = get_vehicle(repository=repository, vehicle_uuid=vehicle_id)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    office_options = [{"id": office.id, "name": office.name} for office in offices]

    return templates.TemplateResponse(
        request=request,
        name="vehicles/form.html",
        context={
            "request": request,
            "title": translate(lang, "vehicles.form_view_title", vehicle_id=vehicle.id),
            "mode": "view",
            "form_action": "#",
            "values": {
                "office_id": str(vehicle.office_id),
                "name": vehicle.name,
                "plate": vehicle.plate or "",
                "lat": "" if vehicle.lat is None else str(vehicle.lat),
                "lng": "" if vehicle.lng is None else str(vehicle.lng),
                "max_capacity": str(vehicle.max_capacity),
            },
            "errors": {},
            "offices": offices,
            "office_options": office_options,
            "lang": lang,
        },
    )
