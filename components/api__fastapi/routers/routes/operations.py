from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from bases.platform.db import get_session
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from components.route_planning.route_planner_service import (
    generate_routes,
    get_route_detail,
    recalculate_route,
    reorder_route_tasks,
)

router = APIRouter()


class OrderedTaskUuidsPayload(BaseModel):
    orderedTaskUuids: list[str]


@router.get("/routes/planning")
def planning_routes_endpoint(
    service_date: date = Query(...),
    office_uuid: str = Query(...),
    session: Session = Depends(get_session),
) -> dict:
    office = session.exec(select(OfficeModel).where(OfficeModel.uuid == office_uuid, OfficeModel.deleted_at.is_(None))).first()
    if office is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")

    routes = session.exec(
        select(RouteModel, VehicleModel)
        .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
        .where(
            RouteModel.office_id == office.id,
            RouteModel.service_date == service_date,
            RouteModel.deleted_at.is_(None),
            VehicleModel.deleted_at.is_(None),
        )
        .order_by(RouteModel.created_at.asc())
    ).all()
    return {
        "data": [
            {
                "uuid": route.uuid,
                "vehicle_name": vehicle.name,
                "status": route.status,
                "total_tasks": route.total_tasks,
                "total_load": route.total_load,
                "total_distance_m": route.total_distance_m,
            }
            for route, vehicle in routes
        ]
    }


@router.post("/routes/generate")
def generate_routes_endpoint(
    service_date: date = Query(...),
    office_uuid: str = Query(...),
    session: Session = Depends(get_session),
) -> dict:
    generate_routes(session=session, service_date=service_date, office_uuid=office_uuid)
    return planning_routes_endpoint(service_date=service_date, office_uuid=office_uuid, session=session)


@router.get("/routes/{route_uuid}/detail")
def route_detail_endpoint(route_uuid: str, session: Session = Depends(get_session)) -> dict:
    detail = get_route_detail(session=session, route_uuid=route_uuid)
    return {
        "route": detail.route,
        "office": detail.office,
        "tasks": [task.__dict__ for task in detail.tasks],
    }


@router.post("/routes/{route_uuid}/recalculate")
def recalculate_route_endpoint(route_uuid: str, session: Session = Depends(get_session)) -> dict:
    detail = recalculate_route(session=session, route_uuid=route_uuid)
    return {
        "route": detail.route,
        "office": detail.office,
        "tasks": [task.__dict__ for task in detail.tasks],
    }


@router.patch("/routes/{route_uuid}/tasks/reorder")
def reorder_route_tasks_endpoint(
    route_uuid: str,
    payload: OrderedTaskUuidsPayload,
    session: Session = Depends(get_session),
) -> dict:
    detail = reorder_route_tasks(session=session, route_uuid=route_uuid, ordered_task_uuids=payload.orderedTaskUuids)
    return {
        "route": detail.route,
        "office": detail.office,
        "tasks": [task.__dict__ for task in detail.tasks],
    }
