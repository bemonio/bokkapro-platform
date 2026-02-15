from fastapi import APIRouter

from components.ui__server_rendered.routers.routes.delete import router as delete_router
from components.ui__server_rendered.routers.routes.edit import router as edit_router
from components.ui__server_rendered.routers.routes.list import router as list_router
from components.ui__server_rendered.routers.routes.new import router as new_router
from components.ui__server_rendered.routers.routes.view import router as view_router

router = APIRouter()
router.include_router(list_router, prefix="/routes")
router.include_router(new_router, prefix="/routes")
router.include_router(view_router, prefix="/routes")
router.include_router(edit_router, prefix="/routes")
router.include_router(delete_router, prefix="/routes")
