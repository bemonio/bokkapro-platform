from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from components.ui__server_rendered.dependencies import get_locale, get_templates
from components.ui__server_rendered.i18n import translate

router = APIRouter()


@router.get("/planning")
def planning_ui(
    request: Request,
    lang: str = Depends(get_locale),
    templates: Jinja2Templates = Depends(get_templates),
):
    return templates.TemplateResponse(
        request=request,
        name="planning/index.html",
        context={
            "request": request,
            "title": translate(lang, "planning.title"),
            "lang": lang,
            "today": date.today().isoformat(),
        },
    )
