from sqlmodel import Session, func, or_, select

from components.app__vehicle.ports import VehicleRepository
from components.domain__vehicle.entities import Vehicle
from components.persistence__sqlmodel.models.office import OfficeModel
from components.persistence__sqlmodel.models.vehicle import VehicleModel
from components.persistence__sqlmodel.repositories.shared.sorting import apply_sorting

VEHICLE_SORT_FIELDS = {
    "id": VehicleModel.id,
    "office_id": VehicleModel.office_id,
    "name": VehicleModel.name,
    "plate": VehicleModel.plate,
    "max_capacity": VehicleModel.max_capacity,
    "created_at": VehicleModel.created_at,
    "updated_at": VehicleModel.updated_at,
}


class VehicleRepositorySqlModel(VehicleRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_entity(self, model: VehicleModel, office: OfficeModel | None = None) -> Vehicle:
        return Vehicle(
            id=model.id,
            uuid=model.uuid,
            tenant_id=model.tenant_id,
            office_id=model.office_id,
            office_uuid=office.uuid if office else None,
            office_name=office.name if office else None,
            name=model.name,
            plate=model.plate,
            lat=model.lat,
            lng=model.lng,
            max_capacity=model.max_capacity,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    def _to_model(self, entity: Vehicle) -> VehicleModel:
        return VehicleModel(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            office_id=entity.office_id,
            name=entity.name,
            plate=entity.plate,
            lat=entity.lat,
            lng=entity.lng,
            max_capacity=entity.max_capacity,
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
    ) -> tuple[list[Vehicle], int]:
        stmt = (
            select(VehicleModel, OfficeModel)
            .join(OfficeModel, VehicleModel.office_id == OfficeModel.id)
            .where(VehicleModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        count_stmt = (
            select(func.count())
            .select_from(VehicleModel)
            .join(OfficeModel, VehicleModel.office_id == OfficeModel.id)
            .where(VehicleModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )

        normalized_search = " ".join(search.split()) if search is not None else None
        if normalized_search:
            term = f"%{normalized_search}%"
            search_clause = or_(
                VehicleModel.name.ilike(term),
                VehicleModel.plate.ilike(term),
                VehicleModel.uuid.ilike(term),
                OfficeModel.name.ilike(term),
                OfficeModel.uuid.ilike(term),
            )
            stmt = stmt.where(search_clause)
            count_stmt = count_stmt.where(search_clause)

        stmt = apply_sorting(stmt, sort=sort, order=order, allowed_fields=VEHICLE_SORT_FIELDS)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = self.session.exec(stmt).all()
        total = self.session.exec(count_stmt).one()
        return [self._to_entity(vehicle, office) for vehicle, office in rows], total

    def get(self, vehicle_id: int) -> Vehicle | None:
        stmt = (
            select(VehicleModel, OfficeModel)
            .join(OfficeModel, VehicleModel.office_id == OfficeModel.id)
            .where(VehicleModel.id == vehicle_id, VehicleModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office = row
        return self._to_entity(model, office)

    def get_by_uuid(self, vehicle_uuid: str) -> Vehicle | None:
        stmt = (
            select(VehicleModel, OfficeModel)
            .join(OfficeModel, VehicleModel.office_id == OfficeModel.id)
            .where(VehicleModel.uuid == vehicle_uuid, VehicleModel.deleted_at.is_(None), OfficeModel.deleted_at.is_(None))
        )
        row = self.session.exec(stmt).first()
        if row is None:
            return None
        model, office = row
        return self._to_entity(model, office)

    def create(self, vehicle: Vehicle) -> Vehicle:
        model = self._to_model(vehicle)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        return self._to_entity(model, office)

    def update(self, vehicle: Vehicle) -> Vehicle:
        model = self.session.get(VehicleModel, vehicle.id)
        if model is None:
            raise ValueError("Vehicle not found during update")

        model.office_id = vehicle.office_id
        model.name = vehicle.name
        model.plate = vehicle.plate
        model.lat = vehicle.lat
        model.lng = vehicle.lng
        model.max_capacity = vehicle.max_capacity
        model.updated_at = vehicle.updated_at

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        office = self.session.get(OfficeModel, model.office_id)
        return self._to_entity(model, office)

    def soft_delete(self, vehicle: Vehicle) -> None:
        model = self.session.get(VehicleModel, vehicle.id)
        if model is None:
            raise ValueError("Vehicle not found during delete")

        model.deleted_at = vehicle.deleted_at
        model.updated_at = vehicle.updated_at
        self.session.add(model)
        self.session.commit()
