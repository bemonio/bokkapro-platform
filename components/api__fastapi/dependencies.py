from fastapi import Depends
from sqlmodel import Session

from bases.platform.db import get_session
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel
from components.persistence__sqlmodel.repositories.tasks_repo import TaskRepositorySqlModel
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel


def get_office_repository(session: Session = Depends(get_session)) -> OfficeRepositorySqlModel:
    return OfficeRepositorySqlModel(session)



def get_vehicle_repository(session: Session = Depends(get_session)) -> VehicleRepositorySqlModel:
    return VehicleRepositorySqlModel(session)


def get_task_repository(session: Session = Depends(get_session)) -> TaskRepositorySqlModel:
    return TaskRepositorySqlModel(session)
