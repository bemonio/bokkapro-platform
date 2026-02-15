from fastapi import FastAPI

from bases.platform.config import get_settings
from components.api__fastapi.routers.offices import router as offices_router
from components.api__fastapi.routers.routes import router as routes_router
from components.api__fastapi.routers.route_tasks import router as route_tasks_router
from components.api__fastapi.routers.tasks import router as tasks_router
from components.api__fastapi.routers.vehicles import router as vehicles_router
from components.ui__server_rendered.routers import router as ui_router

settings = get_settings()

app = FastAPI(
    title="Bokkapro Platform",
    docs_url="/docs" if settings.swagger_ui_enabled else None,
    redoc_url="/redoc" if settings.swagger_ui_enabled else None,
    openapi_url="/openapi.json",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(offices_router)
app.include_router(vehicles_router)
app.include_router(tasks_router)
app.include_router(routes_router)
app.include_router(route_tasks_router)

app.include_router(ui_router, include_in_schema=False)
