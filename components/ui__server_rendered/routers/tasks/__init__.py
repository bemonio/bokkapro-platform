from fastapi import APIRouter

from components.ui__server_rendered.routers.tasks.delete import router as delete_router
from components.ui__server_rendered.routers.tasks.edit import router as edit_router
from components.ui__server_rendered.routers.tasks.list import router as list_router
from components.ui__server_rendered.routers.tasks.new import router as new_router
from components.ui__server_rendered.routers.tasks.view import router as view_router

router = APIRouter()
router.include_router(list_router, prefix="/tasks")
router.include_router(new_router, prefix="/tasks")
router.include_router(view_router, prefix="/tasks")
router.include_router(edit_router, prefix="/tasks")
router.include_router(delete_router, prefix="/tasks")
