from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_vehicle_repository
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
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="vehicles/form.html",
        context={
            "request": request,
            "title": translate(lang, "vehicles.form_new_title"),
            "mode": "create",
            "form_action": "/vehicles/new",
            "values": {"office_id": "", "office_uuid": "", "name": "", "plate": "", "lat": "", "lng": "", "max_capacity": "0"},
            "errors": {},
            "office_selected": None,
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
    form_data = await request.form()
    office_uuid = str(form_data.get("office_uuid") or "").strip()
    mutable_form_data = dict(form_data)
    selected_office = None

    if office_uuid:
        selected_office = office_repository.get_by_uuid(office_uuid)
        if selected_office is not None:
            mutable_form_data["office_id"] = str(selected_office.id)

    payload, values, errors = create_from_form(mutable_form_data)
    if selected_office is None:
        errors["office_id"] = translate(lang, "vehicles.office_not_found")

    if payload is None or selected_office is None:
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
                "office_selected": None if selected_office is None else {"uuid": selected_office.uuid, "name": selected_office.name},
                "lang": lang,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    create_vehicle(
        repository=repository,
        office_id=payload.office_id,
        name=payload.name,
        plate=payload.plate,
        lat=payload.lat,
        lng=payload.lng,
        max_capacity=payload.max_capacity,
    )
    return RedirectResponse(url=f"/vehicles?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
