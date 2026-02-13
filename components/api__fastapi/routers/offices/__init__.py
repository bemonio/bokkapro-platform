from fastapi import APIRouter

from components.api__fastapi.routers.offices.create import router as create_router
from components.api__fastapi.routers.offices.delete import router as delete_router
from components.api__fastapi.routers.offices.get import router as get_router
from components.api__fastapi.routers.offices.list import router as list_router
from components.api__fastapi.routers.offices.update import router as update_router

router = APIRouter(tags=["offices"])
api_router = APIRouter(prefix="/api")
api_v1_router = APIRouter(prefix="/api/v1")

for prefix_router in (api_router, api_v1_router):
    prefix_router.include_router(list_router)
    prefix_router.include_router(get_router)
    prefix_router.include_router(create_router)
    prefix_router.include_router(update_router)
    prefix_router.include_router(delete_router)

router.include_router(api_router)
router.include_router(api_v1_router)
