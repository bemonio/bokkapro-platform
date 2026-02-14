from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_vehicle_repository
from components.app__vehicle.use_cases.get_vehicle import get_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{vehicle_uuid}")
def view_vehicle(
    vehicle_uuid: str,
    request: Request,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        vehicle = get_vehicle(repository=repository, vehicle_uuid=vehicle_uuid)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    selected_office = office_repository.get(vehicle.office_id)

    return templates.TemplateResponse(
        request=request,
        name="vehicles/form.html",
        context={
            "request": request,
            "title": translate(lang, "vehicles.form_view_title"),
            "mode": "view",
            "entity_uuid": vehicle.uuid,
            "form_action": "#",
            "values": {
                "office_id": str(vehicle.office_id),
                "office_uuid": "" if selected_office is None else selected_office.uuid,
                "name": vehicle.name,
                "plate": vehicle.plate or "",
                "lat": "" if vehicle.lat is None else str(vehicle.lat),
                "lng": "" if vehicle.lng is None else str(vehicle.lng),
                "max_capacity": str(vehicle.max_capacity),
            },
            "errors": {},
            "office_selected": None if selected_office is None else {"uuid": selected_office.uuid, "name": selected_office.name},
            "lang": lang,
        },
    )
