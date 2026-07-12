import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
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
logger = logging.getLogger(__name__)
VEHICLE_RESPONSES = {
    status.HTTP_200_OK: {"description": "Vehicle operation completed."},
    status.HTTP_201_CREATED: {"description": "Vehicle created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid vehicle request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    status.HTTP_409_CONFLICT: {"description": "Vehicle conflict."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error."},
}


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


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List vehicles",
    description=(
        "Returns a paginated fleet inventory. Use filters to review availability, "
        "vehicle class, or search by registration number/name before dispatching."
    ),
    responses=VEHICLE_RESPONSES,
)
def get_vehicles(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[
        VehicleStatus | None,
        Query(alias="status", description="Filter vehicles by operational status."),
    ] = None,
    vehicle_type: Annotated[
        str | None,
        Query(description="Filter by commercial vehicle type, such as Container Truck."),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search registration number or vehicle name."),
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description=(
                "Sort field: registration_number, vehicle_name, odometer, or "
                "created_at."
            ),
        ),
    ] = "created_at",
    sort_order: Annotated[
        str,
        Query(description="Sort direction: asc or desc."),
    ] = "desc",
    page: Annotated[int, Query(ge=1, description="One-based page number.")] = 1,
    limit: Annotated[
        int,
        Query(ge=1, description="Maximum records to return per page."),
    ] = 10,
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


@router.get(
    "/{vehicle_id}",
    response_model=SuccessResponse[VehicleResponse],
    summary="Get vehicle",
    description=(
        "Returns a single fleet vehicle, including status, capacity, odometer, "
        "and acquisition cost."
    ),
    responses=VEHICLE_RESPONSES,
)
def get_vehicle(
    vehicle_id: Annotated[int, Path(gt=0, description="Unique vehicle identifier.")],
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
    summary="Create vehicle",
    description="Creates a vehicle record for fleet operations. Requires Fleet Manager access.",
    responses=VEHICLE_RESPONSES,
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

    logger.info("Vehicle CRUD create successful for vehicle_id=%s", vehicle.id)
    return SuccessResponse(
        message="Vehicle created",
        data=VehicleResponse.model_validate(vehicle),
    )


@router.put(
    "/{vehicle_id}",
    response_model=SuccessResponse[VehicleResponse],
    summary="Update vehicle",
    description="Updates vehicle profile, capacity, odometer, cost, or availability status.",
    responses=VEHICLE_RESPONSES,
)
def update_vehicle(
    vehicle_id: Annotated[int, Path(gt=0, description="Unique vehicle identifier.")],
    payload: VehicleUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[VehicleResponse]:
    service = VehicleService(db)
    try:
        vehicle = service.update_vehicle(vehicle_id, payload)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    logger.info("Vehicle CRUD update successful for vehicle_id=%s", vehicle.id)
    return SuccessResponse(
        message="Vehicle updated",
        data=VehicleResponse.model_validate(vehicle),
    )


@router.delete(
    "/{vehicle_id}",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Delete vehicle",
    description=(
        "Deletes a vehicle record when allowed by existing fleet rules. Requires "
        "Fleet Manager access."
    ),
    responses=VEHICLE_RESPONSES,
)
def delete_vehicle(
    vehicle_id: Annotated[int, Path(gt=0, description="Unique vehicle identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[dict[str, Any]]:
    service = VehicleService(db)
    try:
        service.delete_vehicle(vehicle_id)
    except Exception as exc:
        _handle_vehicle_service_error(exc)

    logger.info("Vehicle CRUD delete successful for vehicle_id=%s", vehicle_id)
    return SuccessResponse(message="Vehicle deleted", data={})
