from fastapi import Depends
from sqlmodel import Session

from bases.platform.db import get_session
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel


def get_office_repository(session: Session = Depends(get_session)) -> OfficeRepositorySqlModel:
    return OfficeRepositorySqlModel(session)
