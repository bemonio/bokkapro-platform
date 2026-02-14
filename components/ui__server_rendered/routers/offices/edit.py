from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.get_office import get_office
from components.app__office.use_cases.update_office import update_office
from components.domain__office.errors import OfficeNotFoundError
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate
from components.ui__server_rendered.routers.offices._helpers import update_from_form

router = APIRouter()


@router.get("/{office_uuid}/edit")
def edit_office_form(
    office_uuid: str,
    request: Request,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        office = get_office(repository=repository, office_uuid=office_uuid)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return templates.TemplateResponse(
        request=request,
        name="offices/form.html",
        context={
            "request": request,
            "title": translate(lang, "offices.form_edit_title"),
            "mode": "edit",
            "entity_uuid": office.uuid,
            "form_action": f"/offices/{office.uuid}/edit",
            "values": {
                "name": office.name,
                "address": office.address or "",
                "lat": "" if office.lat is None else str(office.lat),
                "lng": "" if office.lng is None else str(office.lng),
                "storage_capacity": str(office.storage_capacity),
            },
            "errors": {},
            "lang": lang,
        },
    )


@router.post("/{office_uuid}/edit")
async def edit_office_ui(
    office_uuid: str,
    request: Request,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    try:
        office = get_office(repository=repository, office_uuid=office_uuid)
    except OfficeNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    form_data = await request.form()
    payload, values, errors = update_from_form(form_data)
    if payload is None or payload.name is None or payload.storage_capacity is None:
        if payload is not None:
            errors["name"] = errors.get("name", translate(lang, "offices.name_required"))
            errors["storage_capacity"] = errors.get("storage_capacity", translate(lang, "offices.storage_required"))
        return templates.TemplateResponse(
            request=request,
            name="offices/form.html",
            context={
                "request": request,
                "title": translate(lang, "offices.form_edit_title"),
                "mode": "edit",
            "entity_uuid": office.uuid,
                "form_action": f"/offices/{office_uuid}/edit",
                "values": values,
                "errors": errors,
                "lang": lang,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    update_office(
        repository=repository,
        office_uuid=office_uuid,
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        storage_capacity=payload.storage_capacity,
    )

    return RedirectResponse(url=f"/offices?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
