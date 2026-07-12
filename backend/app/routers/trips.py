from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, require_roles
from app.database.database import get_db
from app.models.enums import TripStatus
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.trip import TripComplete, TripCreate, TripResponse, TripUpdate
from app.services.driver_service import DriverNotFoundError
from app.services.trip_service import (
    TripConflictError,
    TripDuplicateError,
    TripNotFoundError,
    TripService,
    TripValidationError,
)
from app.services.vehicle_service import VehicleNotFoundError

router = APIRouter()

TRIP_MANAGEMENT_ROLES = ("Fleet Manager", "Dispatcher")


def _handle_trip_service_error(exc: Exception) -> None:
    if isinstance(exc, (TripNotFoundError, VehicleNotFoundError, DriverNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, (TripDuplicateError, TripConflictError)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if isinstance(exc, TripValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get("", response_model=SuccessResponse[dict[str, Any]])
def get_trips(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[TripStatus | None, Query(alias="status")] = None,
    vehicle_id: int | None = None,
    driver_id: int | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
) -> SuccessResponse[dict[str, Any]]:
    service = TripService(db)
    try:
        trips = service.get_all_trips(
            status=status_filter,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(message="Trips retrieved", data=trips)


@router.get("/{trip_id}", response_model=SuccessResponse[TripResponse])
def get_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.get_trip_by_id(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip retrieved",
        data=TripResponse.model_validate(trip),
    )


@router.post(
    "",
    response_model=SuccessResponse[TripResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_trip(
    payload: TripCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.create_trip(payload)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip created",
        data=TripResponse.model_validate(trip),
    )


@router.put("/{trip_id}", response_model=SuccessResponse[TripResponse])
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.update_draft_trip(trip_id, payload)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip updated",
        data=TripResponse.model_validate(trip),
    )


@router.delete("/{trip_id}", response_model=SuccessResponse[dict[str, Any]])
def delete_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[dict[str, Any]]:
    service = TripService(db)
    try:
        service.delete_draft_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(message="Trip deleted", data={})


@router.patch("/{trip_id}/dispatch", response_model=SuccessResponse[TripResponse])
def dispatch_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.dispatch_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip dispatched",
        data=TripResponse.model_validate(trip),
    )


@router.patch("/{trip_id}/complete", response_model=SuccessResponse[TripResponse])
def complete_trip(
    trip_id: int,
    payload: TripComplete,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.complete_trip(trip_id, payload)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip completed",
        data=TripResponse.model_validate(trip),
    )


@router.patch("/{trip_id}/cancel", response_model=SuccessResponse[TripResponse])
def cancel_trip(
    trip_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.cancel_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(
        message="Trip cancelled",
        data=TripResponse.model_validate(trip),
    )
