<<<<<<< HEAD
from typing import Annotated, Any
=======
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, require_roles
from app.database.database import get_db
from app.models.enums import DriverStatus
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.driver import DriverCreate, DriverListResponse, DriverResponse, DriverUpdate
from app.services.driver_service import DriverService
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218

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


<<<<<<< HEAD
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

=======
@router.get("", response_model=SuccessResponse[DriverListResponse])
def list_drivers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
    status_filter: Annotated[DriverStatus | None, Query(alias="status")] = None,
    license_type: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    search: Annotated[str | None, Query(min_length=1, max_length=255)] = None,
    sort_by: Annotated[Literal["driver_name", "license_number", "created_at"], Query()] = "created_at",
    sort_order: Annotated[Literal["asc", "desc"], Query()] = "asc",
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> SuccessResponse[DriverListResponse]:
    drivers = DriverService(db).list_drivers(
        status_filter=status_filter,
        license_type=license_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
    return SuccessResponse(message="Drivers retrieved", data=drivers)


@router.get("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def get_driver(
    driver_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[DriverResponse]:
<<<<<<< HEAD
    service = DriverService(db)
    try:
        driver = service.get_driver_by_id(driver_id)
    except Exception as exc:
        _handle_driver_service_error(exc)

    return SuccessResponse(
        message="Driver retrieved",
        data=DriverResponse.model_validate(driver),
=======
    return SuccessResponse(
        message="Driver retrieved",
        data=DriverService(db).get_driver(driver_id),
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
    )


@router.post(
    "",
    response_model=SuccessResponse[DriverResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_driver(
    payload: DriverCreate,
    db: Annotated[Session, Depends(get_db)],
<<<<<<< HEAD
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
=======
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[DriverResponse]:
    return SuccessResponse(
        message="Driver created",
        data=DriverService(db).create_driver(payload),
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
    )


@router.put("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Annotated[Session, Depends(get_db)],
<<<<<<< HEAD
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
=======
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[DriverResponse]:
    return SuccessResponse(
        message="Driver updated",
        data=DriverService(db).update_driver(driver_id, payload),
    )


@router.delete("/{driver_id}", response_model=SuccessResponse[dict[str, int]])
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
def delete_driver(
    driver_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
<<<<<<< HEAD
) -> SuccessResponse[dict[str, Any]]:
    service = DriverService(db)
    try:
        service.delete_driver(driver_id)
    except Exception as exc:
        _handle_driver_service_error(exc)

    return SuccessResponse(message="Driver deleted", data={})
=======
) -> SuccessResponse[dict[str, int]]:
    DriverService(db).delete_driver(driver_id)
    return SuccessResponse(message="Driver deleted", data={"id": driver_id})
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
