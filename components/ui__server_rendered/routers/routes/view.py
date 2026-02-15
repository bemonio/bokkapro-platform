from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_route_repository, get_vehicle_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__route.use_cases.get_route import get_route
from components.app__vehicle.use_cases.list_vehicles import list_vehicles
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/{route_uuid}")
def view_route_ui(
    route_uuid: str,
    request: Request,
    repository: RouteRepositorySqlModel = Depends(get_route_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    vehicle_repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    route = get_route(repository=repository, route_uuid=route_uuid)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    vehicles, _ = list_vehicles(repository=vehicle_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    return templates.TemplateResponse(
        request=request,
        name="routes/form.html",
        context={
            "request": request,
            "title": translate(lang, "routes.form_view_title"),
            "mode": "view",
            "entity_uuid": route.uuid,
            "form_action": "",
            "values": {
                **{k: "" if getattr(route, k) is None else str(getattr(route, k)) for k in ["office_id", "vehicle_id", "service_date", "status", "total_tasks", "total_distance_m", "total_duration_s", "total_load"]},
                "office_name": route.office_name or "",
                "vehicle_name": route.vehicle_name or "",
            },
            "errors": {},
            "office_options": [{"id": office.id, "name": office.name} for office in offices],
            "vehicle_options": [{"id": vehicle.id, "name": vehicle.name} for vehicle in vehicles],
            "lang": lang,
        },
    )
