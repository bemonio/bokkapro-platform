from fastapi import APIRouter

from components.ui__server_rendered.routers.route_tasks.delete import router as delete_router
from components.ui__server_rendered.routers.route_tasks.edit import router as edit_router
from components.ui__server_rendered.routers.route_tasks.list import router as list_router
from components.ui__server_rendered.routers.route_tasks.new import router as new_router
from components.ui__server_rendered.routers.route_tasks.view import router as view_router

router = APIRouter()
router.include_router(list_router, prefix="/route-tasks")
router.include_router(new_router, prefix="/route-tasks")
router.include_router(view_router, prefix="/route-tasks")
router.include_router(edit_router, prefix="/route-tasks")
router.include_router(delete_router, prefix="/route-tasks")
