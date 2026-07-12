import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, require_roles
from app.database.database import get_db
from app.models.enums import DriverStatus
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate
from app.services.driver_service import (
    DriverDuplicateError,
    DriverNotFoundError,
    DriverService,
    DriverValidationError,
)

router = APIRouter()
logger = logging.getLogger(__name__)
DRIVER_RESPONSES = {
    status.HTTP_200_OK: {"description": "Driver operation completed."},
    status.HTTP_201_CREATED: {"description": "Driver created."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid driver request."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Driver not found."},
    status.HTTP_409_CONFLICT: {"description": "Driver conflict."},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"description": "Validation error."},
}


def _handle_driver_service_error(exc: Exception) -> None:
    if isinstance(exc, DriverNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, DriverDuplicateError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if isinstance(exc, DriverValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get(
    "",
    response_model=SuccessResponse[dict[str, Any]],
    summary="List drivers",
    description=(
        "Returns a paginated driver roster with licensing, safety score, and "
        "availability filters for dispatch planning."
    ),
    responses=DRIVER_RESPONSES,
)
def get_drivers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[
        DriverStatus | None,
        Query(
            alias="status",
            description="Filter drivers by availability or employment status.",
        ),
    ] = None,
    license_category: Annotated[
        str | None,
        Query(description="Filter by license category such as HMV, LMV, or HAZMAT."),
    ] = None,
    search: Annotated[
        str | None,
        Query(description="Search driver name or license number."),
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description=(
                "Sort field: name, license_expiry_date, safety_score, or "
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
    service = DriverService(db)
    try:
        drivers = service.get_all_drivers(
            status=status_filter,
            license_category=license_category,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit,
        )
    except Exception as exc:
        _handle_driver_service_error(exc)

    return SuccessResponse(message="Drivers retrieved", data=drivers)


@router.get(
    "/{driver_id}",
    response_model=SuccessResponse[DriverResponse],
    summary="Get driver",
    description=(
        "Returns a single driver profile, including license, safety score, and "
        "current status."
    ),
    responses=DRIVER_RESPONSES,
)
def get_driver(
    driver_id: Annotated[int, Path(gt=0, description="Unique driver identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[DriverResponse]:
    service = DriverService(db)
    try:
        driver = service.get_driver_by_id(driver_id)
    except Exception as exc:
        _handle_driver_service_error(exc)

    return SuccessResponse(
        message="Driver retrieved",
        data=DriverResponse.model_validate(driver),
    )


@router.post(
    "",
    response_model=SuccessResponse[DriverResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create driver",
    description=(
        "Creates a driver profile for fleet operations. Requires Fleet Manager "
        "or Safety Officer access."
    ),
    responses=DRIVER_RESPONSES,
)
def create_driver(
    payload: DriverCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[
        User,
        Depends(require_roles("Fleet Manager", "Safety Officer")),
    ],
) -> SuccessResponse[DriverResponse]:
    service = DriverService(db)
    try:
        driver = service.create_driver(payload)
    except Exception as exc:
        _handle_driver_service_error(exc)

    logger.info("Driver CRUD create successful for driver_id=%s", driver.id)
    return SuccessResponse(
        message="Driver created",
        data=DriverResponse.model_validate(driver),
    )


@router.put(
    "/{driver_id}",
    response_model=SuccessResponse[DriverResponse],
    summary="Update driver",
    description="Updates driver contact, licensing, safety score, or availability details.",
    responses=DRIVER_RESPONSES,
)
def update_driver(
    driver_id: Annotated[int, Path(gt=0, description="Unique driver identifier.")],
    payload: DriverUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[
        User,
        Depends(require_roles("Fleet Manager", "Safety Officer")),
    ],
) -> SuccessResponse[DriverResponse]:
    service = DriverService(db)
    try:
        driver = service.update_driver(driver_id, payload)
    except Exception as exc:
        _handle_driver_service_error(exc)

    logger.info("Driver CRUD update successful for driver_id=%s", driver.id)
    return SuccessResponse(
        message="Driver updated",
        data=DriverResponse.model_validate(driver),
    )


@router.delete(
    "/{driver_id}",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Delete driver",
    description="Deletes a driver record when allowed by existing driver management rules.",
    responses=DRIVER_RESPONSES,
)
def delete_driver(
    driver_id: Annotated[int, Path(gt=0, description="Unique driver identifier.")],
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[dict[str, Any]]:
    service = DriverService(db)
    try:
        service.delete_driver(driver_id)
    except Exception as exc:
        _handle_driver_service_error(exc)

    logger.info("Driver CRUD delete successful for driver_id=%s", driver_id)
    return SuccessResponse(message="Driver deleted", data={})
