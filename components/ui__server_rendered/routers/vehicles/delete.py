from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from components.api__fastapi.dependencies import get_vehicle_repository
from components.app__vehicle.use_cases.delete_vehicle import delete_vehicle
from components.domain__vehicle.errors import VehicleNotFoundError
from components.persistence__sqlmodel.repositories.vehicles_repo import VehicleRepositorySqlModel

router = APIRouter()


@router.post("/{vehicle_id}/delete")
def delete_vehicle_ui(
    vehicle_id: int,
    lang: str = "en",
    repository: VehicleRepositorySqlModel = Depends(get_vehicle_repository),
):
    try:
        delete_vehicle(repository=repository, vehicle_uuid=vehicle_id)
    except VehicleNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RedirectResponse(url=f"/vehicles?lang={lang}", status_code=status.HTTP_303_SEE_OTHER)
