from fastapi import APIRouter, Depends, Request

from components.api__fastapi.dependencies import get_vehicle_repository
from components.api__fastapi.schemas.common import ListQueryParams, get_vehicle_list_query_params
from components.api__fastapi.schemas.common.pagination import Meta, PaginationMeta
from components.api__fastapi.schemas.vehicles.base import VehicleListResponse, VehicleRead
from components.app__vehicle.use_cases.list_vehicles import list_vehicles
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.get("/vehicles", response_model=VehicleListResponse)
def list_vehicles_endpoint(
    request: Request,
    params: ListQueryParams = Depends(get_vehicle_list_query_params),
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
) -> VehicleListResponse:
    items, total = list_vehicles(
        repository=repository,
        page=params.page,
        page_size=params.page_size,
        search=params.search,
        sort=params.sort,
        order=params.order,
    )

    filters = {"search": params.search} if params.search else None
    sort = {"by": params.sort, "order": params.order} if "sort" in request.query_params or "order" in request.query_params else None

    return VehicleListResponse(
        data=[VehicleRead.model_validate(item) for item in items],
        meta=Meta(
            pagination=PaginationMeta.from_values(total=total, page=params.page, page_size=params.page_size),
            filters=filters,
            sort=sort,
        ),
    )
