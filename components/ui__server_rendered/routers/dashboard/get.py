from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/")
def get_dashboard(
    request: Request,
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "title": translate(lang, "dashboard.title"), "lang": lang},
    )
