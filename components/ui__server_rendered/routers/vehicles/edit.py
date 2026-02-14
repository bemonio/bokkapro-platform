from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository, get_vehicle_repository
from components.app__vehicle.use_cases.get_vehicle import get_vehicle
from components.app__vehicle.use_cases.update_vehicle import update_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.vehicles._helpers import update_from_form

router = APIRouter()


@router.get("/{vehicle_uuid}/edit")
def edit_vehicle_form(
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
            "title": translate(lang, "vehicles.form_edit_title"),
            "mode": "edit",
            "entity_uuid": vehicle.uuid,
            "form_action": f"/vehicles/{vehicle.uuid}/edit",
            "values": {
                "office_id": str(vehicle.office_id),
                "office_uuid": "" if selected_office is None else selected_office.uuid,
                "office_name": "" if selected_office is None else selected_office.name,
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


@router.post("/{vehicle_uuid}/edit")
async def edit_vehicle_ui(
    vehicle_uuid: str,
    request: Request,
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
    office_repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        get_vehicle(repository=repository, vehicle_uuid=vehicle_uuid)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    form_data = await request.form()
    office_uuid = str(form_data.get("office_uuid") or "").strip()
    mutable_form_data = dict(form_data)
    selected_office = None

    if office_uuid:
        selected_office = office_repository.get_by_uuid(office_uuid)
        if selected_office is not None:
            mutable_form_data["office_id"] = str(selected_office.id)

    payload, values, errors = update_from_form(mutable_form_data)
    if selected_office is None:
        errors["office_id"] = translate(lang, "vehicles.office_not_found")

    if payload is None or selected_office is None:
        return templates.TemplateResponse(
            request=request,
            name="vehicles/form.html",
            context={
                "request": request,
                "title": translate(lang, "vehicles.form_edit_title"),
                "mode": "edit",
                "entity_uuid": vehicle_uuid,
                "form_action": f"/vehicles/{vehicle_uuid}/edit",
                "values": values,
                "errors": errors,
                "office_selected": None if selected_office is None else {"uuid": selected_office.uuid, "name": selected_office.name},
                "lang": lang,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    update_vehicle(
        repository=repository,
        vehicle_uuid=vehicle_uuid,
        office_id=payload.office_id,
        name=payload.name,
        plate=payload.plate,
        lat=payload.lat,
        lng=payload.lng,
        max_capacity=payload.max_capacity,
    )
    return RedirectResponse(url=f"/vehicles?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
