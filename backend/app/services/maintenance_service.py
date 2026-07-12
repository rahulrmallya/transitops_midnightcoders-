from typing import Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.enums import VehicleStatus
from app.models.maintenance_log import MaintenanceLog
from app.schemas.maintenance import MaintenanceLogCreate, MaintenanceLogResponse
from app.services.vehicle_service import VehicleService


class MaintenanceNotFoundError(Exception):
    pass


class MaintenanceValidationError(Exception):
    pass


class MaintenanceConflictError(Exception):
    pass


class MaintenanceService:
    sortable_fields = {
        "start_date": MaintenanceLog.start_date,
        "end_date": MaintenanceLog.end_date,
        "cost": MaintenanceLog.cost,
        "created_at": MaintenanceLog.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vehicle_service = VehicleService(db)

    def create_maintenance_record(
        self,
        payload: MaintenanceLogCreate,
    ) -> MaintenanceLog:
        self._validate_maintenance_data(payload.model_dump())
        vehicle = self.vehicle_service.get_vehicle_by_id(payload.vehicle_id)
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise MaintenanceConflictError(
                "Vehicle must be available before maintenance can start"
            )

        data = payload.model_dump()
        data["status"] = "OPEN"

        try:
            maintenance_log = MaintenanceLog(**data)
            vehicle.status = VehicleStatus.IN_SHOP
            self.db.add(maintenance_log)
            self.db.commit()
            self.db.refresh(maintenance_log)
        except Exception:
            self.db.rollback()
            raise

        return maintenance_log

    def get_maintenance_record_by_id(self, maintenance_id: int) -> MaintenanceLog:
        maintenance_log = self.db.get(MaintenanceLog, maintenance_id)
        if maintenance_log is None:
            raise MaintenanceNotFoundError("Maintenance record not found")

        return maintenance_log

    def get_all_maintenance_records(
        self,
        *,
        vehicle_id: int | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise MaintenanceValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise MaintenanceValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise MaintenanceValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise MaintenanceValidationError("Invalid sort order")

        statement = select(MaintenanceLog)
        count_statement = select(func.count()).select_from(MaintenanceLog)

        filters = []
        if vehicle_id is not None:
            filters.append(MaintenanceLog.vehicle_id == vehicle_id)
        if status:
            filters.append(MaintenanceLog.status == status)

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        maintenance_logs = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [
                MaintenanceLogResponse.model_validate(log)
                for log in maintenance_logs
            ],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def close_maintenance(self, maintenance_id: int) -> MaintenanceLog:
        maintenance_log = self.get_maintenance_record_by_id(maintenance_id)
        if maintenance_log.status == "CLOSED":
            raise MaintenanceConflictError("Maintenance record is already closed")

        vehicle = self.vehicle_service.get_vehicle_by_id(maintenance_log.vehicle_id)

        try:
            maintenance_log.status = "CLOSED"
            if vehicle.status != VehicleStatus.RETIRED:
                vehicle.status = VehicleStatus.AVAILABLE
            self.db.commit()
            self.db.refresh(maintenance_log)
        except Exception:
            self.db.rollback()
            raise

        return maintenance_log

    def _validate_maintenance_data(self, data: dict[str, Any]) -> None:
        if data["cost"] < 0:
            raise MaintenanceValidationError("Maintenance cost must be greater than or equal to 0")
        if data["end_date"] < data["start_date"]:
            raise MaintenanceValidationError("End date must be on or after start date")
