import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
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
logger = logging.getLogger(__name__)

TRIP_MANAGEMENT_ROLES = ("Fleet Manager", "Dispatcher")
TRIP_RESPONSES = {
    status.HTTP_200_OK: {"description": "Trip operation completed."},
    status.HTTP_201_CREATED: {"description": "Trip created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid trip request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Trip, vehicle, or driver not found."},
    status.HTTP_409_CONFLICT: {"description": "Trip state conflict."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error."},
}


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


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List trips",
    description=(
        "Returns paginated trips across the operational lifecycle. Filter by "
        "status, assigned vehicle, assigned driver, or search lane and trip code."
    ),
    responses=TRIP_RESPONSES,
)
def get_trips(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[
        TripStatus | None,
        Query(alias="status", description="Filter trips by lifecycle status."),
    ] = None,
    vehicle_id: Annotated[
        int | None,
        Query(gt=0, description="Filter trips assigned to a specific vehicle."),
    ] = None,
    driver_id: Annotated[
        int | None,
        Query(gt=0, description="Filter trips assigned to a specific driver."),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search by trip code, source, or destination."),
    ] = None,
    sort_by: Annotated[
        str,
        Query(description="Sort field: trip_code, source, destination, or created_at."),
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


@router.get(
    "/{trip_id}",
    response_model=SuccessResponse[TripResponse],
    summary="Get trip",
    description=(
        "Returns a single trip with planned metrics, actual completion metrics, "
        "assignments, and status."
    ),
    responses=TRIP_RESPONSES,
)
def get_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
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
    summary="Create trip",
    description=(
        "Creates a draft trip. Dispatch validations are applied later when the "
        "dispatch endpoint is called."
    ),
    responses=TRIP_RESPONSES,
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


@router.put(
    "/{trip_id}",
    response_model=SuccessResponse[TripResponse],
    summary="Update draft trip",
    description=(
        "Updates an existing draft trip. Trips that have already been "
        "dispatched cannot be edited here."
    ),
    responses=TRIP_RESPONSES,
)
def update_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
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


@router.delete(
    "/{trip_id}",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Delete draft trip",
    description="Deletes an existing draft trip before it enters dispatch operations.",
    responses=TRIP_RESPONSES,
)
def delete_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[dict[str, Any]]:
    service = TripService(db)
    try:
        service.delete_draft_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    return SuccessResponse(message="Trip deleted", data={})


@router.patch(
    "/{trip_id}/dispatch",
    response_model=SuccessResponse[TripResponse],
    summary="Dispatch trip",
    description=(
        "Dispatches a draft trip after validating vehicle availability, driver "
        "availability, active license, and cargo capacity. Vehicle and driver "
        "statuses move to ON_TRIP in the same transaction."
    ),
    responses=TRIP_RESPONSES,
)
def dispatch_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.dispatch_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    logger.info("Trip dispatch successful for trip_id=%s", trip.id)
    return SuccessResponse(
        message="Trip dispatched",
        data=TripResponse.model_validate(trip),
    )


@router.patch(
    "/{trip_id}/complete",
    response_model=SuccessResponse[TripResponse],
    summary="Complete trip",
    description=(
        "Completes a dispatched trip with actual distance, fuel consumed, and "
        "revenue. Vehicle and driver are released to AVAILABLE and the vehicle "
        "odometer is incremented."
    ),
    responses=TRIP_RESPONSES,
)
def complete_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
    payload: TripComplete,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.complete_trip(trip_id, payload)
    except Exception as exc:
        _handle_trip_service_error(exc)

    logger.info("Trip completion successful for trip_id=%s", trip.id)
    return SuccessResponse(
        message="Trip completed",
        data=TripResponse.model_validate(trip),
    )


@router.patch(
    "/{trip_id}/cancel",
    response_model=SuccessResponse[TripResponse],
    summary="Cancel trip",
    description=(
        "Cancels a dispatched trip and restores the assigned vehicle and "
        "driver to AVAILABLE."
    ),
    responses=TRIP_RESPONSES,
)
def cancel_trip(
    trip_id: Annotated[int, Path(gt=0, description="Unique trip identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*TRIP_MANAGEMENT_ROLES))],
) -> SuccessResponse[TripResponse]:
    service = TripService(db)
    try:
        trip = service.cancel_trip(trip_id)
    except Exception as exc:
        _handle_trip_service_error(exc)

    logger.info("Trip cancellation successful for trip_id=%s", trip.id)
    return SuccessResponse(
        message="Trip cancelled",
        data=TripResponse.model_validate(trip),
    )
