from fastapi import FastAPI

from components.api__fastapi.routers.offices import router as offices_router
from components.api__fastapi.routers.vehicles import router as vehicles_router
from components.ui__server_rendered.routers import router as ui_router

app = FastAPI(title="Bokkapro Platform")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(offices_router)
app.include_router(vehicles_router)

app.include_router(ui_router)
