from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.enums import DriverStatus, TripStatus, VehicleStatus
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.schemas.trip import TripComplete, TripCreate, TripResponse, TripUpdate
from app.services.driver_service import DriverService
from app.services.vehicle_service import VehicleService


class TripNotFoundError(Exception):
    pass


class TripDuplicateError(Exception):
    pass


class TripValidationError(Exception):
    pass


class TripConflictError(Exception):
    pass


class TripService:
    sortable_fields = {
        "trip_code": Trip.trip_code,
        "source": Trip.source,
        "destination": Trip.destination,
        "created_at": Trip.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vehicle_service = VehicleService(db)
        self.driver_service = DriverService(db)

    def create_trip(self, payload: TripCreate) -> Trip:
        data = payload.model_dump()
        if payload.status not in {None, TripStatus.DRAFT}:
            raise TripValidationError("Trips must be created as draft")

        data["status"] = TripStatus.DRAFT
        data["actual_distance"] = data["actual_distance"] or 0
        data["fuel_consumed"] = data["fuel_consumed"] or 0
        data["revenue"] = data["revenue"] or 0

        self._validate_trip_data(data)
        self._ensure_trip_code_unique(payload.trip_code)

        self.vehicle_service.get_vehicle_by_id(payload.vehicle_id)
        self.driver_service.get_driver_by_id(payload.driver_id)

        trip = Trip(**data)
        self.db.add(trip)
        try:
            self.db.commit()
            self.db.refresh(trip)
        except Exception:
            self.db.rollback()
            raise
        return trip

    def get_trip_by_id(self, trip_id: int) -> Trip:
        trip = self.db.get(Trip, trip_id)
        if trip is None:
            raise TripNotFoundError("Trip not found")

        return trip

    def get_all_trips(
        self,
        *,
        status: TripStatus | None = None,
        vehicle_id: int | None = None,
        driver_id: int | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise TripValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise TripValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise TripValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise TripValidationError("Invalid sort order")

        statement = select(Trip)
        count_statement = select(func.count()).select_from(Trip)

        filters = []
        if status is not None:
            filters.append(Trip.status == status)
        if vehicle_id is not None:
            filters.append(Trip.vehicle_id == vehicle_id)
        if driver_id is not None:
            filters.append(Trip.driver_id == driver_id)
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Trip.trip_code.ilike(search_pattern),
                    Trip.source.ilike(search_pattern),
                    Trip.destination.ilike(search_pattern),
                )
            )

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        trips = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [TripResponse.model_validate(trip) for trip in trips],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def update_draft_trip(self, trip_id: int, payload: TripUpdate) -> Trip:
        trip = self.get_trip_by_id(trip_id)
        if trip.status != TripStatus.DRAFT:
            raise TripConflictError("Only draft trips can be updated")

        update_data = payload.model_dump(exclude_unset=True)
        self._validate_trip_data(update_data)

        if update_data.get("status") not in {None, TripStatus.DRAFT}:
            raise TripValidationError("Draft update cannot change trip status")
        update_data.pop("status", None)

        trip_code = update_data.get("trip_code")
        if trip_code is not None:
            self._ensure_trip_code_unique(trip_code, trip_id)

        if update_data.get("vehicle_id") is not None:
            self.vehicle_service.get_vehicle_by_id(update_data["vehicle_id"])
        if update_data.get("driver_id") is not None:
            self.driver_service.get_driver_by_id(update_data["driver_id"])

        for field, value in update_data.items():
            setattr(trip, field, value)

        try:
            self.db.commit()
            self.db.refresh(trip)
        except Exception:
            self.db.rollback()
            raise
        return trip

    def delete_draft_trip(self, trip_id: int) -> None:
        trip = self.get_trip_by_id(trip_id)
        if trip.status != TripStatus.DRAFT:
            raise TripConflictError("Only draft trips can be deleted")

        self.db.delete(trip)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def dispatch_trip(self, trip_id: int) -> Trip:
        trip = self.get_trip_by_id(trip_id)
        if trip.status != TripStatus.DRAFT:
            raise TripConflictError("Only draft trips can be dispatched")

        vehicle = self.vehicle_service.get_vehicle_by_id(trip.vehicle_id)
        driver = self.driver_service.get_driver_by_id(trip.driver_id)
        self._validate_dispatch_rules(trip, vehicle, driver)

        try:
            trip.status = TripStatus.DISPATCHED
            vehicle.status = VehicleStatus.ON_TRIP
            driver.status = DriverStatus.ON_TRIP
            self.db.commit()
            self.db.refresh(trip)
        except Exception:
            self.db.rollback()
            raise

        return trip

    def complete_trip(self, trip_id: int, payload: TripComplete) -> Trip:
        trip = self.get_trip_by_id(trip_id)
        if trip.status != TripStatus.DISPATCHED:
            raise TripConflictError("Only dispatched trips can be completed")

        vehicle = self.vehicle_service.get_vehicle_by_id(trip.vehicle_id)
        driver = self.driver_service.get_driver_by_id(trip.driver_id)

        try:
            trip.actual_distance = payload.actual_distance
            trip.fuel_consumed = payload.fuel_consumed
            trip.revenue = payload.revenue
            trip.status = TripStatus.COMPLETED
            vehicle.status = VehicleStatus.AVAILABLE
            driver.status = DriverStatus.AVAILABLE
            vehicle.odometer = self._to_decimal(vehicle.odometer) + self._to_decimal(
                payload.actual_distance
            )
            self.db.commit()
            self.db.refresh(trip)
        except Exception:
            self.db.rollback()
            raise

        return trip

    def cancel_trip(self, trip_id: int) -> Trip:
        trip = self.get_trip_by_id(trip_id)
        if trip.status != TripStatus.DISPATCHED:
            raise TripConflictError("Only dispatched trips can be cancelled")

        vehicle = self.vehicle_service.get_vehicle_by_id(trip.vehicle_id)
        driver = self.driver_service.get_driver_by_id(trip.driver_id)

        try:
            trip.status = TripStatus.CANCELLED
            vehicle.status = VehicleStatus.AVAILABLE
            driver.status = DriverStatus.AVAILABLE
            self.db.commit()
            self.db.refresh(trip)
        except Exception:
            self.db.rollback()
            raise

        return trip

    def _ensure_trip_code_unique(
        self,
        trip_code: str,
        trip_id: int | None = None,
    ) -> None:
        statement = select(Trip).where(Trip.trip_code == trip_code)
        if trip_id is not None:
            statement = statement.where(Trip.id != trip_id)

        existing_trip = self.db.scalar(statement)
        if existing_trip is not None:
            raise TripDuplicateError("Trip code already exists")

    def _validate_trip_data(self, data: dict[str, Any]) -> None:
        if (
            "status" in data
            and data["status"] is not None
            and data["status"] not in set(TripStatus)
        ):
            raise TripValidationError("Invalid trip status")
        if "trip_code" in data and data["trip_code"] is None:
            raise TripValidationError("Trip code cannot be null")
        if "source" in data and data["source"] is None:
            raise TripValidationError("Source cannot be null")
        if "destination" in data and data["destination"] is None:
            raise TripValidationError("Destination cannot be null")
        if "vehicle_id" in data and data["vehicle_id"] is None:
            raise TripValidationError("Vehicle cannot be null")
        if "driver_id" in data and data["driver_id"] is None:
            raise TripValidationError("Driver cannot be null")
        if "cargo_weight" in data and data["cargo_weight"] <= 0:
            raise TripValidationError("Cargo weight must be greater than 0")
        if "planned_distance" in data and data["planned_distance"] <= 0:
            raise TripValidationError("Planned distance must be greater than 0")
        if "actual_distance" in data and data["actual_distance"] is None:
            raise TripValidationError("Actual distance cannot be null")
        if "actual_distance" in data and data["actual_distance"] < 0:
            raise TripValidationError("Actual distance must be greater than or equal to 0")
        if "fuel_consumed" in data and data["fuel_consumed"] is None:
            raise TripValidationError("Fuel consumed cannot be null")
        if "fuel_consumed" in data and data["fuel_consumed"] < 0:
            raise TripValidationError("Fuel consumed must be greater than or equal to 0")
        if "revenue" in data and data["revenue"] is None:
            raise TripValidationError("Revenue cannot be null")
        if "revenue" in data and data["revenue"] < 0:
            raise TripValidationError("Revenue must be greater than or equal to 0")

    def _validate_dispatch_rules(
        self,
        trip: Trip,
        vehicle: Vehicle,
        driver: Driver,
    ) -> None:
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise TripConflictError("Vehicle must be available before dispatch")
        if driver.status != DriverStatus.AVAILABLE:
            raise TripConflictError("Driver must be available before dispatch")
        if driver.license_expiry_date < date.today():
            raise TripConflictError("Driver license has expired")
        if self._to_decimal(trip.cargo_weight) > self._to_decimal(
            vehicle.max_load_capacity
        ):
            raise TripConflictError("Cargo weight exceeds vehicle capacity")

    def _to_decimal(self, value: Any) -> Decimal:
        return Decimal(str(value))
