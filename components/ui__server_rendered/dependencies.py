from pathlib import Path

from fastapi.templating import Jinja2Templates


def get_templates() -> Jinja2Templates:
    templates_dir = Path(__file__).resolve().parent / "templates"
    return Jinja2Templates(directory=str(templates_dir))
