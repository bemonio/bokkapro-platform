from fastapi import APIRouter

from components.ui__server_rendered.routers.vehicles.delete import router as delete_router
from components.ui__server_rendered.routers.vehicles.edit import router as edit_router
from components.ui__server_rendered.routers.vehicles.list import router as list_router
from components.ui__server_rendered.routers.vehicles.new import router as new_router
from components.ui__server_rendered.routers.vehicles.view import router as view_router

router = APIRouter()
router.include_router(list_router, prefix="/vehicles")
router.include_router(new_router, prefix="/vehicles")
router.include_router(view_router, prefix="/vehicles")
router.include_router(edit_router, prefix="/vehicles")
router.include_router(delete_router, prefix="/vehicles")
