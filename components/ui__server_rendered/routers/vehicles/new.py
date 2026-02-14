from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_vehicle_repository
from components.app__office.use_cases.list_offices import list_offices
from components.app__vehicle.use_cases.create_vehicle import create_vehicle
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.vehicles._helpers import create_from_form

router = APIRouter()


@router.get("/new")
def new_vehicle_form(
    request: Request,
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    return templates.TemplateResponse(
        request=request,
        name="vehicles/form.html",
        context={
            "request": request,
            "title": translate(lang, "vehicles.form_new_title"),
            "mode": "create",
            "form_action": "/vehicles/new",
            "values": {"office_id": "", "name": "", "plate": "", "max_capacity": "0"},
            "errors": {},
            "offices": offices,
            "lang": lang,
        },
    )


@router.post("/new")
async def create_vehicle_ui(
    request: Request,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    offices, _ = list_offices(repository=office_repository, page=1, page_size=100, search=None, sort="name", order="asc")
    form_data = await request.form()
    payload, values, errors = create_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="vehicles/form.html",
            context={
                "request": request,
                "title": translate(lang, "vehicles.form_new_title"),
                "mode": "create",
                "form_action": "/vehicles/new",
                "values": values,
                "errors": errors,
                "offices": offices,
                "lang": lang,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    vehicle = create_vehicle(
        repository=repository,
        office_id=payload.office_id,
        name=payload.name,
        plate=payload.plate,
        max_capacity=payload.max_capacity,
    )
    return RedirectResponse(url=f"/vehicles/{vehicle.id}?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
