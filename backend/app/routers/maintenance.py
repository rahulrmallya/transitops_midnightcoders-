import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.database import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.maintenance import MaintenanceLogCreate, MaintenanceLogResponse
from app.services.maintenance_service import (
    MaintenanceConflictError,
    MaintenanceNotFoundError,
    MaintenanceService,
    MaintenanceValidationError,
)
from app.services.vehicle_service import VehicleNotFoundError

router = APIRouter()
logger = logging.getLogger(__name__)
MAINTENANCE_RESPONSES = {
    status.HTTP_200_OK: {"description": "Maintenance operation completed."},
    status.HTTP_201_CREATED: {"description": "Maintenance record created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid maintenance request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Maintenance record or vehicle not found."},
    status.HTTP_409_CONFLICT: {"description": "Maintenance state conflict."},
    status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error."},
}


def _handle_maintenance_service_error(exc: Exception) -> None:
    if isinstance(exc, (MaintenanceNotFoundError, VehicleNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, MaintenanceConflictError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if isinstance(exc, MaintenanceValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List maintenance records",
    description="Returns paginated maintenance records with optional filters and sorting.",
    responses=MAINTENANCE_RESPONSES,
)
def get_maintenance_records(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
    vehicle_id: int | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
) -> SuccessResponse[dict[str, Any]]:
    service = MaintenanceService(db)
    try:
        maintenance_records = service.get_all_maintenance_records(
            vehicle_id=vehicle_id,
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_maintenance_service_error(exc)

    return SuccessResponse(
        message="Maintenance records retrieved",
        data=maintenance_records,
    )


@router.get(
    "/{maintenance_id}",
    response_model=SuccessResponse[MaintenanceLogResponse],
    summary="Get maintenance record",
    description="Returns one maintenance record by ID.",
    responses=MAINTENANCE_RESPONSES,
)
def get_maintenance_record(
    maintenance_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[MaintenanceLogResponse]:
    service = MaintenanceService(db)
    try:
        maintenance_record = service.get_maintenance_record_by_id(maintenance_id)
    except Exception as exc:
        _handle_maintenance_service_error(exc)

    return SuccessResponse(
        message="Maintenance record retrieved",
        data=MaintenanceLogResponse.model_validate(maintenance_record),
    )


@router.post(
    "",
    response_model=SuccessResponse[MaintenanceLogResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create maintenance record",
    description="Creates an open maintenance record using existing vehicle availability rules.",
    responses=MAINTENANCE_RESPONSES,
)
def create_maintenance_record(
    payload: MaintenanceLogCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[MaintenanceLogResponse]:
    service = MaintenanceService(db)
    try:
        maintenance_record = service.create_maintenance_record(payload)
    except Exception as exc:
        _handle_maintenance_service_error(exc)

    logger.info(
        "Maintenance created for maintenance_id=%s vehicle_id=%s",
        maintenance_record.id,
        maintenance_record.vehicle_id,
    )
    return SuccessResponse(
        message="Maintenance record created",
        data=MaintenanceLogResponse.model_validate(maintenance_record),
    )


@router.patch(
    "/{maintenance_id}/close",
    response_model=SuccessResponse[MaintenanceLogResponse],
    summary="Close maintenance record",
    description="Closes an open maintenance record and releases the vehicle when allowed.",
    responses=MAINTENANCE_RESPONSES,
)
def close_maintenance(
    maintenance_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[MaintenanceLogResponse]:
    service = MaintenanceService(db)
    try:
        maintenance_record = service.close_maintenance(maintenance_id)
    except Exception as exc:
        _handle_maintenance_service_error(exc)

    logger.info(
        "Maintenance closed for maintenance_id=%s vehicle_id=%s",
        maintenance_record.id,
        maintenance_record.vehicle_id,
    )
    return SuccessResponse(
        message="Maintenance record closed",
        data=MaintenanceLogResponse.model_validate(maintenance_record),
    )
