from sqlmodel import Session, func, or_, select

from components.app__task.ports import TaskRepository
from components.domain__task.entities import Task
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.task import TaskModel
from components.persistence__sqlmodel.repositories.shared.sorting import apply_sorting

TASK_SORT_FIELDS = {
    "id": TaskModel.id,
    "office_id": TaskModel.office_id,
    "type": TaskModel.type,
    "status": TaskModel.status,
    "priority": TaskModel.priority,
    "reference": TaskModel.reference,
    "service_duration_minutes": TaskModel.service_duration_minutes,
    "load_units": TaskModel.load_units,
    "created_at": TaskModel.created_at,
    "updated_at": TaskModel.updated_at,
}


class TaskRepositorySqlModel(TaskRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, model: TaskModel, office: OfficeModel | None = None) -> Task:
        return Task(
            id=model.id,
            uuid=model.uuid,
            tenant_id=model.tenant_id,
            office_id=model.office_id,
            office_uuid=office.uuid if office else None,
            office_name=office.name if office else None,
            type=model.type,
            status=model.status,
            lat=model.lat,
            lng=model.lng,
            address=model.address,
            time_window_start=model.time_window_start,
            time_window_end=model.time_window_end,
            service_duration_minutes=model.service_duration_minutes,
            load_units=model.load_units,
            priority=model.priority,
            reference=model.reference,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: Task) -> TaskModel:
        return TaskModel(**entity.__dict__)

    def list(self, page: int, page_size: int, search: str | None, sort: str, order: str) -> tuple[list[Task], int]:
        stmt = (
            select(TaskModel, OfficeModel)
            .join(OfficeModel, TaskModel.office_id == OfficeModel.id)
            .where(TaskModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        count_stmt = (
            select(func.count())
            .select_from(TaskModel)
            .join(OfficeModel, TaskModel.office_id == OfficeModel.id)
            .where(TaskModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        normalized_search = " ".join(search.split()) if search is not None else None
        if normalized_search:
            term = f"%{normalized_search}%"
            clause = or_(
                TaskModel.type.ilike(term),
                TaskModel.status.ilike(term),
                TaskModel.priority.ilike(term),
                TaskModel.reference.ilike(term),
                TaskModel.address.ilike(term),
                OfficeModel.name.ilike(term),
                TaskModel.uuid.ilike(term),
            )
            stmt = stmt.where(clause)
            count_stmt = count_stmt.where(clause)
        stmt = apply_sorting(stmt, sort=sort, order=order, allowed_fields=TASK_SORT_FIELDS)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = self.session.exec(stmt).all()
        total = self.session.exec(count_stmt).one()
        return [self._to_entity(task, office) for task, office in rows], total

    def get(self, task_id: int) -> Task | None:
        stmt = (
            select(TaskModel, OfficeModel)
            .join(OfficeModel, TaskModel.office_id == OfficeModel.id)
            .where(TaskModel.id == task_id, TaskModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office = row
        return self._to_entity(model, office)

    def get_by_uuid(self, task_uuid: str) -> Task | None:
        stmt = (
            select(TaskModel, OfficeModel)
            .join(OfficeModel, TaskModel.office_id == OfficeModel.id)
            .where(TaskModel.uuid == task_uuid, TaskModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office = row
        return self._to_entity(model, office)

    def create(self, task: Task) -> Task:
        model = self._to_model(task)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        return self._to_entity(model, office)

    def update(self, task: Task) -> Task:
        model = self.session.get(TaskModel, task.id)
        if model is None:
            raise ValueError("Task not found during update")
        for field in (
            "office_id", "type", "status", "lat", "lng", "address", "time_window_start", "time_window_end",
            "service_duration_minutes", "load_units", "priority", "reference", "notes", "updated_at"
        ):
            setattr(model, field, getattr(task, field))
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        return self._to_entity(model, office)

    def soft_delete(self, task: Task) -> None:
        model = self.session.get(TaskModel, task.id)
        if model is None:
            raise ValueError("Task not found during delete")
        model.deleted_at = task.deleted_at
        model.updated_at = task.updated_at
        self.session.add(model)
        self.session.commit()
