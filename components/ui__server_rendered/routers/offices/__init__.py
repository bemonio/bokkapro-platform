from fastapi import APIRouter

from components.ui__server_rendered.routers.offices.delete import router as delete_router
from components.ui__server_rendered.routers.offices.edit import router as edit_router
from components.ui__server_rendered.routers.offices.list import router as list_router
from components.ui__server_rendered.routers.offices.new import router as new_router
from components.ui__server_rendered.routers.offices.view import router as view_router

router = APIRouter(prefix="/ui")
router.include_router(list_router, prefix="/offices")
router.include_router(new_router, prefix="/offices")
router.include_router(view_router, prefix="/offices")
router.include_router(edit_router, prefix="/offices")
router.include_router(delete_router, prefix="/offices")
