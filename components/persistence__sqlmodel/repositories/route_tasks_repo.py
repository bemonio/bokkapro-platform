from sqlmodel import Session, func, or_, select

from components.app__route_task.ports import RouteTaskRepository
from components.domain__route_task.entities import RouteTask
from components.persistence__sqlmodel.models.route_task import RouteTaskModel
from components.persistence__sqlmodel.repositories.shared.sorting import apply_sorting

ROUTE_TASK_SORT_FIELDS = {
    "id": RouteTaskModel.id,
    "route_uuid": RouteTaskModel.route_uuid,
    "task_uuid": RouteTaskModel.task_uuid,
    "sequence_order": RouteTaskModel.sequence_order,
    "status": RouteTaskModel.status,
    "created_at": RouteTaskModel.created_at,
    "updated_at": RouteTaskModel.updated_at,
}


class RouteTaskRepositorySqlModel(RouteTaskRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, model: RouteTaskModel) -> RouteTask:
        return RouteTask(
            id=model.id,
            uuid=model.uuid,
            tenant_id=model.tenant_id,
            route_uuid=model.route_uuid,
            task_uuid=model.task_uuid,
            sequence_order=model.sequence_order,
            planned_arrival_at=model.planned_arrival_at,
            planned_departure_at=model.planned_departure_at,
            actual_arrival_at=model.actual_arrival_at,
            actual_departure_at=model.actual_departure_at,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: RouteTask) -> RouteTaskModel:
        return RouteTaskModel(**entity.__dict__)

    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[RouteTask], int]:
        stmt = select(RouteTaskModel).where(RouteTaskModel.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(RouteTaskModel).where(RouteTaskModel.deleted_at.is_(None))
        normalized_search = " ".join(search.split()) if search is not None else None
        if normalized_search:
            term = f"%{normalized_search}%"
            clause = or_(
                RouteTaskModel.uuid.ilike(term),
                RouteTaskModel.route_uuid.ilike(term),
                RouteTaskModel.task_uuid.ilike(term),
                RouteTaskModel.status.ilike(term),
            )
            stmt = stmt.where(clause)
            count_stmt = count_stmt.where(clause)

        stmt = apply_sorting(stmt, sort=sort, order=order, allowed_fields=ROUTE_TASK_SORT_FIELDS)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        models = self.session.exec(stmt).all()
        total = self.session.exec(count_stmt).one()
        return [self._to_entity(model) for model in models], total

    def get(self, route_task_id: int) -> RouteTask | None:
        stmt = select(RouteTaskModel).where(RouteTaskModel.id == route_task_id, RouteTaskModel.deleted_at.is_(None))
        model = self.session.exec(stmt).first()
        return self._to_entity(model) if model else None

    def get_by_uuid(self, route_task_uuid: str) -> RouteTask | None:
        stmt = select(RouteTaskModel).where(RouteTaskModel.uuid == route_task_uuid, RouteTaskModel.deleted_at.is_(None))
        model = self.session.exec(stmt).first()
        return self._to_entity(model) if model else None

    def create(self, route_task: RouteTask) -> RouteTask:
        model = self._to_model(route_task)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def update(self, route_task: RouteTask) -> RouteTask:
        model = self.session.get(RouteTaskModel, route_task.id)
        if model is None:
            raise ValueError("Route task not found during update")
        for field in (
            "route_uuid", "task_uuid", "sequence_order", "planned_arrival_at", "planned_departure_at",
            "actual_arrival_at", "actual_departure_at", "status", "updated_at"
        ):
            setattr(model, field, getattr(route_task, field))
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def soft_delete(self, route_task: RouteTask) -> None:
        model = self.session.get(RouteTaskModel, route_task.id)
        if model is None:
            raise ValueError("Route task not found during delete")
        model.deleted_at = route_task.deleted_at
        model.updated_at = route_task.updated_at
        self.session.add(model)
        self.session.commit()
