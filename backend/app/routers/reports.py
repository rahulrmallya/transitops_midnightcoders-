from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.database.database import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.report_service import ReportService, ReportValidationError
from app.services.vehicle_service import VehicleNotFoundError

router = APIRouter()

REPORT_ROLES = ("Fleet Manager", "Financial Analyst")
REPORT_RESPONSES = {
    status.HTTP_200_OK: {"description": "Report retrieved."},
    status.HTTP_400_BAD_REQUEST: {"description": "Invalid report filters."},
    status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
    status.HTTP_403_FORBIDDEN: {"description": "Insufficient role permissions."},
    status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
}


def _handle_report_service_error(exc: Exception) -> None:
    if isinstance(exc, VehicleNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, ReportValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    raise exc


@router.get(
    "/dashboard",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Get dashboard report",
    description="Returns high-level operational metrics for dashboards.",
    responses=REPORT_RESPONSES,
)
def get_dashboard_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*REPORT_ROLES))],
    vehicle_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SuccessResponse[dict[str, Any]]:
    service = ReportService(db)
    try:
        metrics = service.get_dashboard_metrics(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception as exc:
        _handle_report_service_error(exc)

    return SuccessResponse(message="Dashboard metrics", data=metrics)


@router.get(
    "/fleet",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Get fleet report",
    description="Returns fleet utilization and distance metrics.",
    responses=REPORT_RESPONSES,
)
def get_fleet_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*REPORT_ROLES))],
    vehicle_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SuccessResponse[dict[str, Any]]:
    service = ReportService(db)
    try:
        fleet_report = service.get_fleet_report(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception as exc:
        _handle_report_service_error(exc)

    return SuccessResponse(message="Fleet report retrieved", data=fleet_report)


@router.get(
    "/cost",
    response_model=SuccessResponse[dict[str, Any]],
    summary="Get cost report",
    description="Returns cost, revenue, and ROI metrics.",
    responses=REPORT_RESPONSES,
)
def get_cost_report(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(*REPORT_ROLES))],
    vehicle_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SuccessResponse[dict[str, Any]]:
    service = ReportService(db)
    try:
        cost_report = service.get_cost_report(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception as exc:
        _handle_report_service_error(exc)

    return SuccessResponse(message="Cost report retrieved", data=cost_report)
