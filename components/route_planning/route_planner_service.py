from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException, status
from sqlmodel import Session, col, select

from bases.platform.time import utc_now
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.route_task import RouteTaskModel
from components.persistence__sqlmodel.models.task import TaskModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from components.route_planning.haversine_matrix import build_distance_matrix
from components.route_planning.ortools_vrp_solver import solve_capacitated_vrp, solve_single_vehicle_route


@dataclass
class RouteTaskPayload:
    route_task_uuid: str
    task_uuid: str
    sequence_order: int
    status: str
    type: str
    address: str | None
    lat: float | None
    lng: float | None
    load_units: int


@dataclass
class RouteDetailPayload:
    route: dict
    office: dict
    tasks: list[RouteTaskPayload]


def _office_query(office_uuid: str):
    return select(OfficeModel).where(OfficeModel.uuid == office_uuid, OfficeModel.deleted_at.is_(None))


def _validate_office_coordinates(office: OfficeModel) -> None:
    if office.lat is None or office.lng is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Office must have valid lat/lng")


def _fetch_vehicles_for_office(session: Session, office: OfficeModel) -> list[VehicleModel]:
    query = select(VehicleModel).where(VehicleModel.deleted_at.is_(None)).order_by(VehicleModel.id.asc())
    if office.tenant_id is not None:
        query = query.where(VehicleModel.tenant_id == office.tenant_id)
    query = query.where(VehicleModel.office_id == office.id)
    return list(session.exec(query).all())


def _build_unassigned_task_query(session: Session, office: OfficeModel, service_date: date):
    assigned_active_subquery = (
        select(RouteTaskModel.task_uuid)
        .join(RouteModel, RouteTaskModel.route_uuid == RouteModel.uuid)
        .where(RouteTaskModel.deleted_at.is_(None), RouteModel.deleted_at.is_(None))
    )

    query = (
        select(TaskModel)
        .where(
            TaskModel.deleted_at.is_(None),
            TaskModel.office_id == office.id,
            col(TaskModel.status).in_(["pending", "scheduled"]),
            col(TaskModel.uuid).not_in(assigned_active_subquery),
        )
        .order_by(TaskModel.created_at.asc())
    )
    if office.tenant_id is not None:
        query = query.where(TaskModel.tenant_id == office.tenant_id)
    return query


def _validate_tasks_for_planning(tasks: list[TaskModel]) -> None:
    invalid_tasks = [task.uuid for task in tasks if task.lat is None or task.lng is None or task.load_units <= 0]
    if invalid_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Tasks must have lat/lng and positive load_units", "invalid_task_uuids": invalid_tasks},
        )


def _route_detail(session: Session, route_uuid: str) -> RouteDetailPayload:
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
    return RouteDetailPayload(
        route={
            "uuid": route.uuid,
            "service_date": route.service_date,
            "status": route.status,
            "total_tasks": route.total_tasks,
            "total_load": route.total_load,
            "total_distance_m": route.total_distance_m,
            "vehicle_name": vehicle.name,
        },
        office={
            "uuid": office.uuid,
            "name": office.name,
            "lat": office.lat,
            "lng": office.lng,
            "address": office.address,
        },
        tasks=[
            RouteTaskPayload(
                route_task_uuid=route_task.uuid,
                task_uuid=task.uuid,
                sequence_order=route_task.sequence_order,
                status=route_task.status,
                type=task.type,
                address=task.address,
                lat=task.lat,
                lng=task.lng,
                load_units=task.load_units,
            )
            for route_task, task in stops
        ],
    )


def generate_routes(session: Session, service_date: date, office_uuid: str) -> list[str]:
    office = session.exec(_office_query(office_uuid)).first()
    if office is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")
    _validate_office_coordinates(office)

    vehicles = _fetch_vehicles_for_office(session, office)
    if not vehicles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No vehicles available for selected office")

    tasks = list(session.exec(_build_unassigned_task_query(session, office, service_date)).all())
    if not tasks:
        return []
    _validate_tasks_for_planning(tasks)

    locations = [(office.lat, office.lng)] + [(task.lat, task.lng) for task in tasks]
    distance_matrix = build_distance_matrix(locations)
    demands = [0] + [task.load_units for task in tasks]
    capacities = [vehicle.max_capacity for vehicle in vehicles]

    solution = solve_capacitated_vrp(distance_matrix=distance_matrix, demands=demands, vehicle_capacities=capacities)
    if not solution.routes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to generate feasible routes")

    created_route_uuids: list[str] = []
    now = utc_now()
    try:
        for planned_route in solution.routes:
            vehicle = vehicles[planned_route.vehicle_index]
            route_tasks = [tasks[task_index] for task_index in planned_route.task_indices]
            route = RouteModel(
                tenant_id=office.tenant_id,
                office_id=office.id,
                vehicle_id=vehicle.id,
                service_date=service_date,
                status="planned",
                total_tasks=len(route_tasks),
                total_load=sum(task.load_units for task in route_tasks),
                total_distance_m=planned_route.distance_m,
                created_at=now,
                updated_at=now,
            )
            session.add(route)
            session.flush()

            for sequence_order, task in enumerate(route_tasks, start=1):
                session.add(
                    RouteTaskModel(
                        tenant_id=office.tenant_id,
                        route_uuid=route.uuid,
                        task_uuid=task.uuid,
                        sequence_order=sequence_order,
                        status="pending",
                        created_at=now,
                        updated_at=now,
                    )
                )

            created_route_uuids.append(route.uuid)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return created_route_uuids


def recalculate_route(session: Session, route_uuid: str) -> RouteDetailPayload:
    route = session.exec(select(RouteModel).where(RouteModel.uuid == route_uuid, RouteModel.deleted_at.is_(None))).first()
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    office = session.exec(select(OfficeModel).where(OfficeModel.id == route.office_id, OfficeModel.deleted_at.is_(None))).first()
    vehicle = session.exec(select(VehicleModel).where(VehicleModel.id == route.vehicle_id, VehicleModel.deleted_at.is_(None))).first()
    if office is None or vehicle is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Route office or vehicle unavailable")
    _validate_office_coordinates(office)

    rows = session.exec(
        select(RouteTaskModel, TaskModel)
        .join(TaskModel, RouteTaskModel.task_uuid == TaskModel.uuid)
        .where(RouteTaskModel.route_uuid == route_uuid, RouteTaskModel.deleted_at.is_(None), TaskModel.deleted_at.is_(None))
        .order_by(RouteTaskModel.sequence_order.asc())
    ).all()
    if not rows:
        return _route_detail(session, route_uuid)

    route_task_models = [row[0] for row in rows]
    tasks = [row[1] for row in rows]
    _validate_tasks_for_planning(tasks)

    locations = [(office.lat, office.lng)] + [(task.lat, task.lng) for task in tasks]
    distance_matrix = build_distance_matrix(locations)
    demands = [0] + [task.load_units for task in tasks]

    plan = solve_single_vehicle_route(distance_matrix=distance_matrix, demands=demands, vehicle_capacity=vehicle.max_capacity)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to recalculate route")

    by_task_uuid = {task.uuid: route_task for route_task, task in zip(route_task_models, tasks, strict=False)}
    ordered_task_uuids = [tasks[task_index].uuid for task_index in plan.task_indices]

    now = utc_now()
    try:
        offset = len(route_task_models) + 10
        for idx, task_uuid in enumerate(ordered_task_uuids, start=1):
            model = by_task_uuid[task_uuid]
            model.sequence_order = idx + offset
            model.updated_at = now
            session.add(model)

        session.flush()

        for idx, task_uuid in enumerate(ordered_task_uuids, start=1):
            model = by_task_uuid[task_uuid]
            model.sequence_order = idx
            model.updated_at = now
            session.add(model)

        route.total_tasks = len(ordered_task_uuids)
        route.total_load = sum(task.load_units for task in tasks)
        route.total_distance_m = plan.distance_m
        route.updated_at = now
        session.add(route)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return _route_detail(session, route_uuid)


def reorder_route_tasks(session: Session, route_uuid: str, ordered_task_uuids: list[str]) -> RouteDetailPayload:
    route = session.exec(select(RouteModel).where(RouteModel.uuid == route_uuid, RouteModel.deleted_at.is_(None))).first()
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    rows = session.exec(
        select(RouteTaskModel, TaskModel)
        .join(TaskModel, RouteTaskModel.task_uuid == TaskModel.uuid)
        .where(RouteTaskModel.route_uuid == route_uuid, RouteTaskModel.deleted_at.is_(None), TaskModel.deleted_at.is_(None))
        .order_by(RouteTaskModel.sequence_order.asc())
    ).all()
    current_task_uuids = [task.uuid for _, task in rows]

    if len(ordered_task_uuids) != len(current_task_uuids) or set(ordered_task_uuids) != set(current_task_uuids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="orderedTaskUuids must match route task list")

    by_task_uuid = {task.uuid: route_task for route_task, task in rows}
    tasks_by_uuid = {task.uuid: task for _, task in rows}
    now = utc_now()

    try:
        offset = len(rows) + 10
        for idx, task_uuid in enumerate(ordered_task_uuids, start=1):
            route_task = by_task_uuid[task_uuid]
            route_task.sequence_order = idx + offset
            route_task.updated_at = now
            session.add(route_task)

        session.flush()

        for idx, task_uuid in enumerate(ordered_task_uuids, start=1):
            route_task = by_task_uuid[task_uuid]
            route_task.sequence_order = idx
            route_task.updated_at = now
            session.add(route_task)

        route.total_tasks = len(rows)
        route.total_load = sum(tasks_by_uuid[task_uuid].load_units for task_uuid in ordered_task_uuids)
        route.updated_at = now
        session.add(route)
        session.commit()
    except Exception:
        session.rollback()
        raise

    return _route_detail(session, route_uuid)


def get_route_detail(session: Session, route_uuid: str) -> RouteDetailPayload:
    return _route_detail(session, route_uuid)
