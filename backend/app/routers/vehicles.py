from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, require_roles
from app.database.database import get_db
from app.models.enums import VehicleStatus
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate
from app.services.vehicle_service import (
    VehicleDuplicateError,
    VehicleNotFoundError,
    VehicleService,
    VehicleValidationError,
)

router = APIRouter()


def _handle_vehicle_service_error(exc: Exception) -> None:
    if isinstance(exc, VehicleNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, VehicleDuplicateError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if isinstance(exc, VehicleValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get("", response_model=SuccessResponse[dict[str, Any]])
def get_vehicles(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[VehicleStatus | None, Query(alias="status")] = None,
    vehicle_type: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
) -> SuccessResponse[dict[str, Any]]:
    service = VehicleService(db)
    try:
        vehicles = service.get_all_vehicles(
            status=status_filter,
            vehicle_type=vehicle_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    return SuccessResponse(message="Vehicles retrieved", data=vehicles)


@router.get("/{vehicle_id}", response_model=SuccessResponse[VehicleResponse])
def get_vehicle(
    vehicle_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[VehicleResponse]:
    service = VehicleService(db)
    try:
        vehicle = service.get_vehicle_by_id(vehicle_id)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    return SuccessResponse(
        message="Vehicle retrieved",
        data=VehicleResponse.model_validate(vehicle),
    )


@router.post(
    "",
    response_model=SuccessResponse[VehicleResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    payload: VehicleCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[VehicleResponse]:
    service = VehicleService(db)
    try:
        vehicle = service.create_vehicle(payload)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    return SuccessResponse(
        message="Vehicle created",
        data=VehicleResponse.model_validate(vehicle),
    )


@router.put("/{vehicle_id}", response_model=SuccessResponse[VehicleResponse])
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[VehicleResponse]:
    service = VehicleService(db)
    try:
        vehicle = service.update_vehicle(vehicle_id, payload)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    return SuccessResponse(
        message="Vehicle updated",
        data=VehicleResponse.model_validate(vehicle),
    )


@router.delete("/{vehicle_id}", response_model=SuccessResponse[dict[str, Any]])
def delete_vehicle(
    vehicle_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[dict[str, Any]]:
    service = VehicleService(db)
    try:
        service.delete_vehicle(vehicle_id)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    return SuccessResponse(message="Vehicle deleted", data={})
