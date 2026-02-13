from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from components.api__fastapi.dependencies import get_office_repository
from components.app__office.use_cases.create_office import create_office
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.ui__server_rendered.dependencies import get_templates
from components.ui__server_rendered.routers.offices._helpers import create_from_form

router = APIRouter()


@router.get("/new")
def new_office_form(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(
        request=request,
        name="offices/form.html",
        context={
            "request": request,
            "title": "New Office",
            "mode": "create",
            "form_action": "/ui/offices/new",
            "values": {"name": "", "address": "", "lat": "", "lng": "", "storage_capacity": "0"},
            "errors": {},
        },
    )


@router.post("/new")
async def create_office_ui(
    request: Request,
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
    templates: Jinja2Templates = Depends(get_templates),
):
    form_data = await request.form()
    payload, values, errors = create_from_form(form_data)
    if payload is None:
        return templates.TemplateResponse(
            request=request,
            name="offices/form.html",
            context={
                "request": request,
                "title": "New Office",
                "mode": "create",
                "form_action": "/ui/offices/new",
                "values": values,
                "errors": errors,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    create_office(
        repository=repository,
        name=payload.name,
        address=payload.address,
        lat=payload.lat,
        lng=payload.lng,
        storage_capacity=payload.storage_capacity,
    )
    return RedirectResponse(url="/ui/offices", status_code=status.HTTP_303_SEE_OTHER)
