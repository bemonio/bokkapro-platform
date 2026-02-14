from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from components.ui__server_rendered.i18n import build_url, normalize_locale, translate


def get_locale(request: Request) -> str:
    return normalize_locale(request.query_params.get("lang"))


def get_templates() -> Jinja2Templates:
    templates_dir = Path(__file__).resolve().parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    templates.env.globals["t"] = translate
    templates.env.globals["url_with_lang"] = build_url
    return templates
