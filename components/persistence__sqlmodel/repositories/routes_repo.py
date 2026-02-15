from sqlmodel import Session, func, or_, select

from components.app__route.ports import RouteRepository
from components.domain__route.entities import Route
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.route import RouteModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from components.persistence__sqlmodel.repositories.shared.sorting import apply_sorting

ROUTE_SORT_FIELDS = {
    "id": RouteModel.id,
    "office_id": RouteModel.office_id,
    "vehicle_id": RouteModel.vehicle_id,
    "service_date": RouteModel.service_date,
    "status": RouteModel.status,
    "total_tasks": RouteModel.total_tasks,
    "total_distance_m": RouteModel.total_distance_m,
    "total_duration_s": RouteModel.total_duration_s,
    "total_load": RouteModel.total_load,
    "created_at": RouteModel.created_at,
    "updated_at": RouteModel.updated_at,
}


class RouteRepositorySqlModel(RouteRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, model: RouteModel, office: OfficeModel | None = None, vehicle: VehicleModel | None = None) -> Route:
        return Route(
            id=model.id,
            uuid=model.uuid,
            tenant_id=model.tenant_id,
            office_id=model.office_id,
            office_uuid=office.uuid if office else None,
            office_name=office.name if office else None,
            vehicle_id=model.vehicle_id,
            vehicle_uuid=vehicle.uuid if vehicle else None,
            vehicle_name=vehicle.name if vehicle else None,
            service_date=model.service_date,
            status=model.status,
            total_tasks=model.total_tasks,
            total_distance_m=model.total_distance_m,
            total_duration_s=model.total_duration_s,
            total_load=model.total_load,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: Route) -> RouteModel:
        return RouteModel(**entity.__dict__)

    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Route], int]:
        stmt = (
            select(RouteModel, OfficeModel, VehicleModel)
            .join(OfficeModel, RouteModel.office_id == OfficeModel.id)
            .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
            .where(RouteModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None), VehicleModel.deleted_at.is_(None))
        )
        count_stmt = (
            select(func.count())
            .select_from(RouteModel)
            .join(OfficeModel, RouteModel.office_id == OfficeModel.id)
            .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
            .where(RouteModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None), VehicleModel.deleted_at.is_(None))
        )
        normalized_search = " ".join(search.split()) if search is not None else None
        if normalized_search:
            term = f"%{normalized_search}%"
            clause = or_(
                RouteModel.status.ilike(term),
                OfficeModel.name.ilike(term),
                VehicleModel.name.ilike(term),
                RouteModel.uuid.ilike(term),
            )
            stmt = stmt.where(clause)
            count_stmt = count_stmt.where(clause)
        stmt = apply_sorting(stmt, sort=sort, order=order, allowed_fields=ROUTE_SORT_FIELDS)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = self.session.exec(stmt).all()
        total = self.session.exec(count_stmt).one()
        return [self._to_entity(route, office, vehicle) for route, office, vehicle in rows], total

    def get(self, route_id: int) -> Route | None:
        stmt = (
            select(RouteModel, OfficeModel, VehicleModel)
            .join(OfficeModel, RouteModel.office_id == OfficeModel.id)
            .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
            .where(RouteModel.id == route_id, RouteModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None), VehicleModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office, vehicle = row
        return self._to_entity(model, office, vehicle)

    def get_by_uuid(self, route_uuid: str) -> Route | None:
        stmt = (
            select(RouteModel, OfficeModel, VehicleModel)
            .join(OfficeModel, RouteModel.office_id == OfficeModel.id)
            .join(VehicleModel, RouteModel.vehicle_id == VehicleModel.id)
            .where(RouteModel.uuid == route_uuid, RouteModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None), VehicleModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office, vehicle = row
        return self._to_entity(model, office, vehicle)

    def create(self, route: Route) -> Route:
        model = self._to_model(route)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        vehicle = self.session.get(VehicleModel, model.vehicle_id)
        return self._to_entity(model, office, vehicle)

    def update(self, route: Route) -> Route:
        model = self.session.get(RouteModel, route.id)
        if model is None:
            raise ValueError("Route not found during update")
        for field in (
            "office_id", "vehicle_id", "service_date", "status", "total_tasks", "total_distance_m", "total_duration_s", "total_load", "updated_at"
        ):
            setattr(model, field, getattr(route, field))
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        vehicle = self.session.get(VehicleModel, model.vehicle_id)
        return self._to_entity(model, office, vehicle)

    def soft_delete(self, route: Route) -> None:
        model = self.session.get(RouteModel, route.id)
        if model is None:
            raise ValueError("Route not found during delete")
        model.deleted_at = route.deleted_at
        model.updated_at = route.updated_at
        self.session.add(model)
        self.session.commit()
