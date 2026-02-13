from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.ui__server_rendered.dependencies import get_templates

router = APIRouter()


@router.get("/")
def get_dashboard(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "title": "Dashboard"},
    )
