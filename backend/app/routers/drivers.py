from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
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


@router.get("", response_model=SuccessResponse[dict[str, Any]])
def get_drivers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[DriverStatus | None, Query(alias="status")] = None,
    license_category: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 10,
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


@router.get("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def get_driver(
    driver_id: int,
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

    return SuccessResponse(
        message="Driver created",
        data=DriverResponse.model_validate(driver),
    )


@router.put("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def update_driver(
    driver_id: int,
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

    return SuccessResponse(
        message="Driver updated",
        data=DriverResponse.model_validate(driver),
    )


@router.delete("/{driver_id}", response_model=SuccessResponse[dict[str, Any]])
def delete_driver(
    driver_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[dict[str, Any]]:
    service = DriverService(db)
    try:
        service.delete_driver(driver_id)
    except Exception as exc:
        _handle_driver_service_error(exc)

    return SuccessResponse(message="Driver deleted", data={})
