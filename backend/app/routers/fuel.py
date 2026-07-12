from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.database import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.fuel import FuelLogCreate, FuelLogResponse
from app.services.fuel_service import (
    FuelLogNotFoundError,
    FuelLogValidationError,
    FuelService,
)
from app.services.vehicle_service import VehicleNotFoundError

router = APIRouter()

FUEL_ROLES = ("Fleet Manager", "Dispatcher")
FUEL_RESPONSES = {
    status.HTTP_200_OK: {"description": "Fuel operation completed."},
    status.HTTP_201_CREATED: {"description": "Fuel log created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid fuel log request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Fuel log or vehicle not found."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error."},
}


def _handle_fuel_service_error(exc: Exception) -> None:
    if isinstance(exc, (FuelLogNotFoundError, VehicleNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, FuelLogValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List fuel logs",
    description="Returns paginated fuel logs for tracking vehicle consumption and operating cost.",
    responses=FUEL_RESPONSES,
)
def get_fuel_logs(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*FUEL_ROLES))],
    vehicle_id: Annotated[
        int | None,
        Query(gt=0, description="Filter fuel logs for a specific vehicle."),
    ] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort field supported by the fuel service."),
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
    service = FuelService(db)
    try:
        fuel_logs = service.get_all_fuel_logs(
            vehicle_id=vehicle_id,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_fuel_service_error(exc)

    return SuccessResponse(message="Fuel logs retrieved", data=fuel_logs)


@router.get(
    "/{fuel_log_id}",
    response_model=SuccessResponse[FuelLogResponse],
    summary="Get fuel log",
    description="Returns a single fuel log with vehicle, quantity, total cost, and fuel date.",
    responses=FUEL_RESPONSES,
)
def get_fuel_log(
    fuel_log_id: Annotated[
        int,
        Path(gt=0, description="Unique fuel log identifier."),
    ],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*FUEL_ROLES))],
) -> SuccessResponse[FuelLogResponse]:
    service = FuelService(db)
    try:
        fuel_log = service.get_fuel_log_by_id(fuel_log_id)
    except Exception as exc:
        _handle_fuel_service_error(exc)

    return SuccessResponse(
        message="Fuel log retrieved",
        data=FuelLogResponse.model_validate(fuel_log),
    )


@router.post(
    "",
    response_model=SuccessResponse[FuelLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create fuel log",
    description=(
        "Creates a fuel log for an existing vehicle. Requires Fleet Manager or "
        "Dispatcher access."
    ),
    responses=FUEL_RESPONSES,
)
def create_fuel_log(
    payload: FuelLogCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*FUEL_ROLES))],
) -> SuccessResponse[FuelLogResponse]:
    service = FuelService(db)
    try:
        fuel_log = service.create_fuel_log(payload)
    except Exception as exc:
        _handle_fuel_service_error(exc)

    return SuccessResponse(
        message="Fuel log created",
        data=FuelLogResponse.model_validate(fuel_log),
    )
