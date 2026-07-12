from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import VehicleStatus
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse, VehicleUpdate


class VehicleNotFoundError(Exception):
    pass


class VehicleDuplicateError(Exception):
    pass


class VehicleValidationError(Exception):
    pass


class VehicleService:
    sortable_fields = {
        "registration_number": Vehicle.registration_number,
        "vehicle_name": Vehicle.vehicle_name,
        "odometer": Vehicle.odometer,
        "created_at": Vehicle.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_vehicle(self, payload: VehicleCreate) -> Vehicle:
        self._validate_vehicle_data(payload.model_dump())
        self._ensure_registration_number_unique(payload.registration_number)

        vehicle = Vehicle(**payload.model_dump())
        self.db.add(vehicle)
        try:
            self.db.commit()
            self.db.refresh(vehicle)
        except Exception:
            self.db.rollback()
            raise
        return vehicle

    def get_vehicle_by_id(self, vehicle_id: int) -> Vehicle:
        vehicle = self.db.get(Vehicle, vehicle_id)
        if vehicle is None:
            raise VehicleNotFoundError("Vehicle not found")

        return vehicle

    def get_all_vehicles(
        self,
        *,
        status: VehicleStatus | None = None,
        vehicle_type: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise VehicleValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise VehicleValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise VehicleValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise VehicleValidationError("Invalid sort order")

        statement = select(Vehicle)
        count_statement = select(func.count()).select_from(Vehicle)

        filters = []
        if status is not None:
            filters.append(Vehicle.status == status)
        if vehicle_type:
            filters.append(Vehicle.vehicle_type == vehicle_type)
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Vehicle.registration_number.ilike(search_pattern),
                    Vehicle.vehicle_name.ilike(search_pattern),
                )
            )

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        vehicles = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [VehicleResponse.model_validate(vehicle) for vehicle in vehicles],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def update_vehicle(self, vehicle_id: int, payload: VehicleUpdate) -> Vehicle:
        vehicle = self.get_vehicle_by_id(vehicle_id)
        update_data = payload.model_dump(exclude_unset=True)
        self._validate_vehicle_data(update_data)

        registration_number = update_data.get("registration_number")
        if registration_number is not None:
            self._ensure_registration_number_unique(registration_number, vehicle_id)

        for field, value in update_data.items():
            setattr(vehicle, field, value)

        try:
            self.db.commit()
            self.db.refresh(vehicle)
        except Exception:
            self.db.rollback()
            raise
        return vehicle

    def delete_vehicle(self, vehicle_id: int) -> None:
        vehicle = self.get_vehicle_by_id(vehicle_id)
        self.db.delete(vehicle)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def _ensure_registration_number_unique(
        self,
        registration_number: str,
        vehicle_id: int | None = None,
    ) -> None:
        statement = select(Vehicle).where(
            Vehicle.registration_number == registration_number
        )
        if vehicle_id is not None:
            statement = statement.where(Vehicle.id != vehicle_id)

        existing_vehicle = self.db.scalar(statement)
        if existing_vehicle is not None:
            raise VehicleDuplicateError("Registration number already exists")

    def _validate_vehicle_data(self, data: dict[str, Any]) -> None:
        if "status" in data and data["status"] not in set(VehicleStatus):
            raise VehicleValidationError("Invalid vehicle status")
        if "max_load_capacity" in data and data["max_load_capacity"] <= 0:
            raise VehicleValidationError("Maximum load capacity must be greater than 0")
        if "odometer" in data and data["odometer"] < 0:
            raise VehicleValidationError("Odometer must be greater than or equal to 0")
        if "acquisition_cost" in data and data["acquisition_cost"] < 0:
            raise VehicleValidationError("Acquisition cost must be greater than or equal to 0")
