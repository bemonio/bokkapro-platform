from fastapi import APIRouter, Depends, Query

from components.api__fastapi.dependencies import get_office_repository
from components.api__fastapi.schemas.offices.base import OfficeListResponse, OfficeRead
from components.app__office.use_cases.list_offices import list_offices
from components.persistence__sqlmodel.repositories.offices_repo import OfficeRepositorySqlModel

router = APIRouter()


@router.get("/offices", response_model=OfficeListResponse)
def list_offices_endpoint(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    repository: OfficeRepositorySqlModel = Depends(get_office_repository),
) -> OfficeListResponse:
    items, total = list_offices(repository=repository, page=page, page_size=page_size, search=search)
    return OfficeListResponse(
        items=[OfficeRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )
