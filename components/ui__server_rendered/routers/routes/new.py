from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_route_repository, get_vehicle_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__route.use_cases.create_route import create_route
from components.app__vehicle.use_cases.list_vehicles import list_vehicles
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.routes_repo import RouteRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.routes._helpers import create_from_form

router = APIRouter()


def _options(office_repository: OfficeRepositorySqlModel, vehicle_repository: VehicleRepositorySqlModel):
    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    vehicles, _ = list_vehicles(repository=vehicle_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    return [{"id": office.id, "name": office.name} for office in offices], [{"id": vehicle.id, "name": vehicle.name} for vehicle in vehicles]


@router.get("/new")
def new_route_form(
    request: Request,
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    vehicle_repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    office_options, vehicle_options = _options(office_repository, vehicle_repository)
    return templates.TemplateResponse(
        request=request,
        name="routes/form.html",
        context={
            "request": request,
            "title": translate(lang, "routes.form_new_title"),
            "mode": "create",
            "form_action": "/routes/new",
            "values": {"office_id": "", "vehicle_id": "", "service_date": "", "status": "draft", "total_tasks": "0", "total_distance_m": "", "total_duration_s": "", "total_load": ""},
            "errors": {},
            "office_options": office_options,
            "vehicle_options": vehicle_options,
            "lang": lang,
        },
    )


@router.post("/new")
async def create_route_ui(
    request: Request,
    repository: RouteRepositorySqlModel = Depends(get_route_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    vehicle_repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    office_options, vehicle_options = _options(office_repository, vehicle_repository)
    form_data = await request.form()
    payload, values, errors = create_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="routes/form.html",
            context={"request": request, "title": translate(lang, "routes.form_new_title"), "mode": "create", "form_action": "/routes/new", "values": values, "errors": errors, "office_options": office_options, "vehicle_options": vehicle_options, "lang": lang},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    create_route(repository=repository, **payload.model_dump())
    return RedirectResponse(url=f"/routes?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
