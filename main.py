from fastapi import FastAPI

from components.api__fastapi.routers.offices import router as offices_router

app = FastAPI(title="Bokkapro Platform")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(offices_router)
