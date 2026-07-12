from typing import Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.fuel_log import FuelLog
from app.schemas.fuel import FuelLogCreate, FuelLogResponse
from app.services.vehicle_service import VehicleService


class FuelLogNotFoundError(Exception):
    pass


class FuelLogValidationError(Exception):
    pass


class FuelService:
    sortable_fields = {
        "fuel_date": FuelLog.fuel_date,
        "liters": FuelLog.liters,
        "cost": FuelLog.cost,
        "created_at": FuelLog.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vehicle_service = VehicleService(db)

    def create_fuel_log(self, payload: FuelLogCreate) -> FuelLog:
        self._validate_fuel_log_data(payload.model_dump())
        self.vehicle_service.get_vehicle_by_id(payload.vehicle_id)

        fuel_log = FuelLog(**payload.model_dump())
        self.db.add(fuel_log)
        try:
            self.db.commit()
            self.db.refresh(fuel_log)
        except Exception:
            self.db.rollback()
            raise
        return fuel_log

    def get_fuel_log_by_id(self, fuel_log_id: int) -> FuelLog:
        fuel_log = self.db.get(FuelLog, fuel_log_id)
        if fuel_log is None:
            raise FuelLogNotFoundError("Fuel log not found")

        return fuel_log

    def get_all_fuel_logs(
        self,
        *,
        vehicle_id: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise FuelLogValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise FuelLogValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise FuelLogValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise FuelLogValidationError("Invalid sort order")

        statement = select(FuelLog)
        count_statement = select(func.count()).select_from(FuelLog)

        if vehicle_id is not None:
            statement = statement.where(FuelLog.vehicle_id == vehicle_id)
            count_statement = count_statement.where(FuelLog.vehicle_id == vehicle_id)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        fuel_logs = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [FuelLogResponse.model_validate(log) for log in fuel_logs],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def _validate_fuel_log_data(self, data: dict[str, Any]) -> None:
        if data["liters"] <= 0:
            raise FuelLogValidationError("Liters must be greater than 0")
        if data["cost"] < 0:
            raise FuelLogValidationError("Fuel cost must be greater than or equal to 0")
