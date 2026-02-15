from sqlmodel import Session, func, or_, select

from components.app__office.ports import OfficeRepository
from components.domain__office.entities import Office
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.repositories.shared.sorting import apply_sorting

OFFICE_SORT_FIELDS = {
    "id": OfficeModel.id,
    "name": OfficeModel.name,
    "address": OfficeModel.address,
    "lat": OfficeModel.lat,
    "lng": OfficeModel.lng,
    "storage_capacity": OfficeModel.storage_capacity,
    "created_at": OfficeModel.created_at,
    "updated_at": OfficeModel.updated_at,
}


class OfficeRepositorySqlModel(OfficeRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, model: OfficeModel) -> Office:
        return Office(
            id=model.id,
            uuid=model.uuid,
            tenant_id=model.tenant_id,
            name=model.name,
            address=model.address,
            place_id=model.place_id,
            lat=model.lat,
            lng=model.lng,
            storage_capacity=model.storage_capacity,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: Office) -> OfficeModel:
        return OfficeModel(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            name=entity.name,
            address=entity.address,
            place_id=entity.place_id,
            lat=entity.lat,
            lng=entity.lng,
            storage_capacity=entity.storage_capacity,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    def list(
        self,
        page: int,
        page_size: int,
        search: str | None,
        sort: str,
        order: str,
    ) -> tuple[list[Office], int]:
        stmt = select(OfficeModel).where(OfficeModel.deleted_at.is_(None))
        count_stmt = select(func.count()).select_from(OfficeModel).where(OfficeModel.deleted_at.is_(None))

        normalized_search = " ".join(search.split()) if search is not None else None
        if normalized_search:
            term = f"%{normalized_search}%"
            search_clause = or_(
                OfficeModel.name.ilike(term),
                OfficeModel.address.ilike(term),
                OfficeModel.uuid.ilike(term),
            )
            stmt = stmt.where(search_clause)
            count_stmt = count_stmt.where(search_clause)

        stmt = apply_sorting(
            stmt,
            sort=sort,
            order=order,
            allowed_fields=OFFICE_SORT_FIELDS,
        )
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        models = self.session.exec(stmt).all()
        total = self.session.exec(count_stmt).one()
        return [self._to_entity(m) for m in models], total

    def get(self, office_id: int) -> Office | None:
        stmt = select(OfficeModel).where(
            OfficeModel.id == office_id,
            OfficeModel.deleted_at.is_(None),
        )
        model = self.session.exec(stmt).first()
        if model is None:
            return None
        return self._to_entity(model)

    def get_by_uuid(self, office_uuid: str) -> Office | None:
        stmt = select(OfficeModel).where(
            OfficeModel.uuid == office_uuid,
            OfficeModel.deleted_at.is_(None),
        )
        model = self.session.exec(stmt).first()
        if model is None:
            return None
        return self._to_entity(model)

    def create(self, office: Office) -> Office:
        model = self._to_model(office)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def update(self, office: Office) -> Office:
        model = self.session.get(OfficeModel, office.id)
        if model is None:
            raise ValueError("Office not found during update")

        model.name = office.name
        model.address = office.address
        model.place_id = office.place_id
        model.lat = office.lat
        model.lng = office.lng
        model.storage_capacity = office.storage_capacity
        model.updated_at = office.updated_at

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def soft_delete(self, office: Office) -> None:
        model = self.session.get(OfficeModel, office.id)
        if model is None:
            raise ValueError("Office not found during delete")

        model.deleted_at = office.deleted_at
        model.updated_at = office.updated_at
        self.session.add(model)
        self.session.commit()
