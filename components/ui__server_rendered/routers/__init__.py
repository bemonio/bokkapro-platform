from fastapi import APIRouter

from components.ui__server_rendered.routers.dashboard.get import router as dashboard_router
from components.ui__server_rendered.routers.offices import router as offices_router
from components.ui__server_rendered.routers.planning import router as planning_router
from components.ui__server_rendered.routers.routes import router as routes_router
from components.ui__server_rendered.routers.route_tasks import router as route_tasks_router
from components.ui__server_rendered.routers.tasks import router as tasks_router
from components.ui__server_rendered.routers.vehicles import router as vehicles_router

router = APIRouter(tags=["ui"])
router.include_router(dashboard_router)
router.include_router(offices_router)
router.include_router(planning_router)
router.include_router(vehicles_router)
router.include_router(tasks_router)
router.include_router(routes_router)

router.include_router(route_tasks_router)
