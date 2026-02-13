from fastapi import APIRouter

from components.api__fastapi.routers.offices.create import router as create_router
from components.api__fastapi.routers.offices.delete import router as delete_router
from components.api__fastapi.routers.offices.get import router as get_router
from components.api__fastapi.routers.offices.list import router as list_router
from components.api__fastapi.routers.offices.update import router as update_router

router = APIRouter(prefix="/api", tags=["offices"])
router.include_router(list_router)
router.include_router(get_router)
router.include_router(create_router)
router.include_router(update_router)
router.include_router(delete_router)
