from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, col, select

from bases.platform.db import get_session
from bases.platform.time import utc_now
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.route_task import RouteTaskModel
from components.persistence__sqlmodel.models.task import TaskModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel

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
    office = session.exec(select(OfficeModel).where(OfficeModel.uuid == office_uuid, OfficeModel.deleted_at.is_(None))).first()
    if office is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")

    existing_route = session.exec(
        select(RouteModel.id)
        .where(RouteModel.office_id == office.id, RouteModel.service_date == service_date, RouteModel.deleted_at.is_(None))
        .limit(1)
    ).first()
    if existing_route is not None:
        return planning_routes_endpoint(service_date=service_date, office_uuid=office_uuid, session=session)

    vehicles = session.exec(
        select(VehicleModel)
        .where(VehicleModel.office_id == office.id, VehicleModel.deleted_at.is_(None))
        .order_by(VehicleModel.id.asc())
    ).all()
    if not vehicles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No vehicles available for selected office")

    tasks = session.exec(
        select(TaskModel)
        .where(
            TaskModel.office_id == office.id,
            TaskModel.deleted_at.is_(None),
            col(TaskModel.status).in_(["pending", "scheduled"]),
        )
        .order_by(TaskModel.created_at.asc())
    ).all()

    assignments: dict[int, list[TaskModel]] = {index: [] for index in range(len(vehicles))}
    for idx, task in enumerate(tasks):
        assignments[idx % len(vehicles)].append(task)

    now = utc_now()
    for idx, vehicle in enumerate(vehicles):
        assigned_tasks = assignments[idx]
        route = RouteModel(
            office_id=office.id,
            vehicle_id=vehicle.id,
            service_date=service_date,
            status="planned",
            total_tasks=len(assigned_tasks),
            total_load=sum(task.load_units for task in assigned_tasks),
            created_at=now,
            updated_at=now,
        )
        session.add(route)
        session.flush()
        for seq, task in enumerate(assigned_tasks, start=1):
            session.add(
                RouteTaskModel(
                    route_uuid=route.uuid,
                    task_uuid=task.uuid,
                    sequence_order=seq,
                    status="pending",
                    created_at=now,
                    updated_at=now,
                )
            )
    session.commit()
    return planning_routes_endpoint(service_date=service_date, office_uuid=office_uuid, session=session)


@router.get("/routes/{route_uuid}/detail")
def route_detail_endpoint(route_uuid: str, session: Session = Depends(get_session)) -> dict:
    row = session.exec(
        select(RouteModel, OfficeModel, VehicleModel)
        .join(OfficeModel, RouteModel.office_id == OfficeModel.id)
        .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
        .where(
            RouteModel.uuid == route_uuid,
            RouteModel.deleted_at.is_(None),
            OfficeModel.deleted_at.is_(None),
            VehicleModel.deleted_at.is_(None),
        )
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    route, office, vehicle = row
    stops = session.exec(
        select(RouteTaskModel, TaskModel)
        .join(TaskModel, RouteTaskModel.task_uuid == TaskModel.uuid)
        .where(RouteTaskModel.route_uuid == route.uuid, RouteTaskModel.deleted_at.is_(None), TaskModel.deleted_at.is_(None))
        .order_by(RouteTaskModel.sequence_order.asc())
    ).all()
    return {
        "route": {
            "uuid": route.uuid,
            "service_date": route.service_date,
            "status": route.status,
            "total_tasks": route.total_tasks,
            "total_load": route.total_load,
            "total_distance_m": route.total_distance_m,
            "vehicle_name": vehicle.name,
        },
        "office": {
            "uuid": office.uuid,
            "name": office.name,
            "lat": office.lat,
            "lng": office.lng,
            "address": office.address,
        },
        "tasks": [
            {
                "route_task_uuid": route_task.uuid,
                "task_uuid": task.uuid,
                "sequence_order": route_task.sequence_order,
                "status": route_task.status,
                "type": task.type,
                "address": task.address,
                "lat": task.lat,
                "lng": task.lng,
                "load_units": task.load_units,
            }
            for route_task, task in stops
        ],
    }


@router.post("/routes/{route_uuid}/recalculate")
def recalculate_route_endpoint(route_uuid: str, session: Session = Depends(get_session)) -> dict:
    route = session.exec(select(RouteModel).where(RouteModel.uuid == route_uuid, RouteModel.deleted_at.is_(None))).first()
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    stops = session.exec(
        select(TaskModel.load_units)
        .join(RouteTaskModel, RouteTaskModel.task_uuid == TaskModel.uuid)
        .where(RouteTaskModel.route_uuid == route_uuid, RouteTaskModel.deleted_at.is_(None), TaskModel.deleted_at.is_(None))
    ).all()
    route.total_tasks = len(stops)
    route.total_load = sum(stops)
    route.updated_at = utc_now()
    session.add(route)
    session.commit()
    return {"ok": True, "message": "Route recalculated"}


@router.patch("/routes/{route_uuid}/tasks/reorder")
def reorder_route_tasks_endpoint(
    route_uuid: str,
    payload: OrderedTaskUuidsPayload,
    session: Session = Depends(get_session),
) -> dict:
    route = session.exec(select(RouteModel).where(RouteModel.uuid == route_uuid, RouteModel.deleted_at.is_(None))).first()
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    route_tasks = session.exec(
        select(RouteTaskModel)
        .where(RouteTaskModel.route_uuid == route_uuid, RouteTaskModel.deleted_at.is_(None))
        .order_by(RouteTaskModel.sequence_order.asc())
    ).all()
    indexed = {item.task_uuid: item for item in route_tasks}
    if len(payload.orderedTaskUuids) != len(route_tasks):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="orderedTaskUuids size mismatch")
    if set(payload.orderedTaskUuids) != set(indexed.keys()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="orderedTaskUuids must match route task list")

    offset = len(route_tasks) + 10
    for idx, task_uuid in enumerate(payload.orderedTaskUuids, start=1):
        model = indexed[task_uuid]
        model.sequence_order = idx + offset
        model.updated_at = utc_now()
        session.add(model)
    session.flush()

    for idx, task_uuid in enumerate(payload.orderedTaskUuids, start=1):
        model = indexed[task_uuid]
        model.sequence_order = idx
        model.updated_at = utc_now()
        session.add(model)

    route.updated_at = utc_now()
    session.add(route)
    session.commit()
    return {"ok": True}
