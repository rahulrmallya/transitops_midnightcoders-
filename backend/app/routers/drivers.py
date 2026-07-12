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


router = APIRouter()


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
    return SuccessResponse(message="Drivers retrieved", data=drivers)


@router.get("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def get_driver(
    driver_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_active_user)],
) -> SuccessResponse[DriverResponse]:
    return SuccessResponse(
        message="Driver retrieved",
        data=DriverService(db).get_driver(driver_id),
    )


@router.post(
    "",
    response_model=SuccessResponse[DriverResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_driver(
    payload: DriverCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[DriverResponse]:
    return SuccessResponse(
        message="Driver created",
        data=DriverService(db).create_driver(payload),
    )


@router.put("/{driver_id}", response_model=SuccessResponse[DriverResponse])
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[DriverResponse]:
    return SuccessResponse(
        message="Driver updated",
        data=DriverService(db).update_driver(driver_id, payload),
    )


@router.delete("/{driver_id}", response_model=SuccessResponse[dict[str, int]])
def delete_driver(
    driver_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("Fleet Manager"))],
) -> SuccessResponse[dict[str, int]]:
    DriverService(db).delete_driver(driver_id)
    return SuccessResponse(message="Driver deleted", data={"id": driver_id})
