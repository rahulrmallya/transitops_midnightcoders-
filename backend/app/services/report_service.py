from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.enums import DriverStatus, TripStatus, VehicleStatus
from app.models.expense import Expense
from app.models.fuel_log import FuelLog
from app.models.maintenance_log import MaintenanceLog
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.services.expense_service import calculate_vehicle_operational_cost
from app.services.vehicle_service import VehicleService


class ReportValidationError(Exception):
    pass


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.vehicle_service = VehicleService(db)

    def get_dashboard_metrics(
        self,
        *,
        vehicle_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, Any]:
        self._validate_filters(vehicle_id, date_from, date_to)

        active_vehicles = self._count_vehicles(
            vehicle_id=vehicle_id,
            excluded_status=VehicleStatus.RETIRED,
        )
        available_vehicles = self._count_vehicles(
            vehicle_id=vehicle_id,
            status=VehicleStatus.AVAILABLE,
        )
        vehicles_on_trip = self._count_vehicles(
            vehicle_id=vehicle_id,
            status=VehicleStatus.ON_TRIP,
        )
        vehicles_in_shop = self._count_vehicles(
            vehicle_id=vehicle_id,
            status=VehicleStatus.IN_SHOP,
        )
        retired_vehicles = self._count_vehicles(
            vehicle_id=vehicle_id,
            status=VehicleStatus.RETIRED,
        )

        drivers_available = self._count_drivers(status=DriverStatus.AVAILABLE)
        drivers_on_trip = self._count_drivers(status=DriverStatus.ON_TRIP)
        drivers_on_duty = drivers_available + drivers_on_trip

        active_trips = self._count_trips(
            vehicle_id=vehicle_id,
            status=TripStatus.DISPATCHED,
            date_from=date_from,
            date_to=date_to,
        )
        completed_trips = self._count_trips(
            vehicle_id=vehicle_id,
            status=TripStatus.COMPLETED,
            date_from=date_from,
            date_to=date_to,
        )
        cancelled_trips = self._count_trips(
            vehicle_id=vehicle_id,
            status=TripStatus.CANCELLED,
            date_from=date_from,
            date_to=date_to,
        )

        total_operational_cost = self._calculate_operational_cost(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_distance = self._sum_trip_field(
            Trip.actual_distance,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_fuel_consumed = self._sum_trip_field(
            Trip.fuel_consumed,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_revenue = self._sum_trip_field(
            Trip.revenue,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        acquisition_cost = self._sum_acquisition_cost(vehicle_id=vehicle_id)

        return {
            "active_vehicles": active_vehicles,
            "available_vehicles": available_vehicles,
            "vehicles_in_shop": vehicles_in_shop,
            "retired_vehicles": retired_vehicles,
            "drivers_on_duty": drivers_on_duty,
            "drivers_available": drivers_available,
            "drivers_on_trip": drivers_on_trip,
            "active_trips": active_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,
            "fleet_utilization": self._percentage(vehicles_on_trip, active_vehicles),
            "total_operational_cost": self._to_float(total_operational_cost),
            "fuel_efficiency": self._ratio(total_distance, total_fuel_consumed),
            "vehicle_roi": self._percentage(
                total_revenue - total_operational_cost,
                acquisition_cost,
            ),
        }

    def get_fleet_report(
        self,
        *,
        vehicle_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, Any]:
        self._validate_filters(vehicle_id, date_from, date_to)

        active_vehicles = self._count_vehicles(
            vehicle_id=vehicle_id,
            excluded_status=VehicleStatus.RETIRED,
        )
        vehicles_on_trip = self._count_vehicles(
            vehicle_id=vehicle_id,
            status=VehicleStatus.ON_TRIP,
        )
        total_distance = self._sum_trip_field(
            Trip.actual_distance,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_fuel_consumed = self._sum_trip_field(
            Trip.fuel_consumed,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )

        return {
            "active_vehicles": active_vehicles,
            "available_vehicles": self._count_vehicles(
                vehicle_id=vehicle_id,
                status=VehicleStatus.AVAILABLE,
            ),
            "vehicles_on_trip": vehicles_on_trip,
            "vehicles_in_shop": self._count_vehicles(
                vehicle_id=vehicle_id,
                status=VehicleStatus.IN_SHOP,
            ),
            "retired_vehicles": self._count_vehicles(
                vehicle_id=vehicle_id,
                status=VehicleStatus.RETIRED,
            ),
            "fleet_utilization": self._percentage(vehicles_on_trip, active_vehicles),
            "total_distance": self._to_float(total_distance),
            "fuel_consumed": self._to_float(total_fuel_consumed),
            "fuel_efficiency": self._ratio(total_distance, total_fuel_consumed),
        }

    def get_cost_report(
        self,
        *,
        vehicle_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, Any]:
        self._validate_filters(vehicle_id, date_from, date_to)

        fuel_cost = self._sum_fuel_cost(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        maintenance_cost = self._sum_maintenance_cost(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        other_expenses = self._sum_expense_amount(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_operational_cost = self._calculate_operational_cost(
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        total_revenue = self._sum_trip_field(
            Trip.revenue,
            vehicle_id=vehicle_id,
            date_from=date_from,
            date_to=date_to,
        )
        acquisition_cost = self._sum_acquisition_cost(vehicle_id=vehicle_id)

        return {
            "fuel_cost": self._to_float(fuel_cost),
            "maintenance_cost": self._to_float(maintenance_cost),
            "other_expenses": self._to_float(other_expenses),
            "total_operational_cost": self._to_float(total_operational_cost),
            "revenue": self._to_float(total_revenue),
            "acquisition_cost": self._to_float(acquisition_cost),
            "vehicle_roi": self._percentage(
                total_revenue - total_operational_cost,
                acquisition_cost,
            ),
        }

    def _validate_filters(
        self,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> None:
        if date_from and date_to and date_from > date_to:
            raise ReportValidationError("date_from must be on or before date_to")
        if vehicle_id is not None:
            self.vehicle_service.get_vehicle_by_id(vehicle_id)

    def _count_vehicles(
        self,
        *,
        vehicle_id: int | None = None,
        status: VehicleStatus | None = None,
        excluded_status: VehicleStatus | None = None,
    ) -> int:
        statement = select(func.count()).select_from(Vehicle)
        if vehicle_id is not None:
            statement = statement.where(Vehicle.id == vehicle_id)
        if status is not None:
            statement = statement.where(Vehicle.status == status)
        if excluded_status is not None:
            statement = statement.where(Vehicle.status != excluded_status)

        return int(self.db.scalar(statement) or 0)

    def _count_drivers(self, *, status: DriverStatus) -> int:
        return int(
            self.db.scalar(
                select(func.count()).select_from(Driver).where(Driver.status == status)
            )
            or 0
        )

    def _count_trips(
        self,
        *,
        vehicle_id: int | None,
        status: TripStatus,
        date_from: date | None,
        date_to: date | None,
    ) -> int:
        statement = select(func.count()).select_from(Trip).where(Trip.status == status)
        statement = self._apply_vehicle_filter(statement, Trip.vehicle_id, vehicle_id)
        statement = self._apply_datetime_filters(
            statement,
            Trip.created_at,
            date_from,
            date_to,
        )

        return int(self.db.scalar(statement) or 0)

    def _sum_trip_field(
        self,
        field: Any,
        *,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Decimal:
        statement = select(func.coalesce(func.sum(field), 0)).select_from(Trip)
        statement = self._apply_vehicle_filter(statement, Trip.vehicle_id, vehicle_id)
        statement = self._apply_datetime_filters(
            statement,
            Trip.created_at,
            date_from,
            date_to,
        )

        return self._to_decimal(self.db.scalar(statement))

    def _sum_fuel_cost(
        self,
        *,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Decimal:
        statement = select(func.coalesce(func.sum(FuelLog.cost), 0)).select_from(FuelLog)
        statement = self._apply_vehicle_filter(statement, FuelLog.vehicle_id, vehicle_id)
        statement = self._apply_date_filters(
            statement,
            FuelLog.fuel_date,
            date_from,
            date_to,
        )

        return self._to_decimal(self.db.scalar(statement))

    def _sum_maintenance_cost(
        self,
        *,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Decimal:
        statement = select(func.coalesce(func.sum(MaintenanceLog.cost), 0)).select_from(
            MaintenanceLog
        )
        statement = self._apply_vehicle_filter(
            statement,
            MaintenanceLog.vehicle_id,
            vehicle_id,
        )
        statement = self._apply_date_filters(
            statement,
            MaintenanceLog.start_date,
            date_from,
            date_to,
        )

        return self._to_decimal(self.db.scalar(statement))

    def _sum_expense_amount(
        self,
        *,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Decimal:
        statement = select(func.coalesce(func.sum(Expense.amount), 0)).select_from(
            Expense
        )
        statement = self._apply_vehicle_filter(statement, Expense.vehicle_id, vehicle_id)
        statement = self._apply_date_filters(
            statement,
            Expense.expense_date,
            date_from,
            date_to,
        )

        return self._to_decimal(self.db.scalar(statement))

    def _sum_acquisition_cost(self, *, vehicle_id: int | None) -> Decimal:
        statement = select(func.coalesce(func.sum(Vehicle.acquisition_cost), 0))
        if vehicle_id is not None:
            statement = statement.where(Vehicle.id == vehicle_id)
        else:
            statement = statement.where(Vehicle.status != VehicleStatus.RETIRED)

        return self._to_decimal(self.db.scalar(statement))

    def _calculate_operational_cost(
        self,
        *,
        vehicle_id: int | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Decimal:
        if date_from is None and date_to is None:
            if vehicle_id is not None:
                return calculate_vehicle_operational_cost(self.db, vehicle_id)

            vehicle_ids = self.db.scalars(select(Vehicle.id)).all()
            return sum(
                (
                    calculate_vehicle_operational_cost(self.db, current_vehicle_id)
                    for current_vehicle_id in vehicle_ids
                ),
                Decimal("0"),
            )

        return (
            self._sum_fuel_cost(
                vehicle_id=vehicle_id,
                date_from=date_from,
                date_to=date_to,
            )
            + self._sum_maintenance_cost(
                vehicle_id=vehicle_id,
                date_from=date_from,
                date_to=date_to,
            )
            + self._sum_expense_amount(
                vehicle_id=vehicle_id,
                date_from=date_from,
                date_to=date_to,
            )
        )

    def _apply_vehicle_filter(
        self,
        statement: Any,
        vehicle_column: Any,
        vehicle_id: int | None,
    ) -> Any:
        if vehicle_id is not None:
            return statement.where(vehicle_column == vehicle_id)
        return statement

    def _apply_date_filters(
        self,
        statement: Any,
        date_column: Any,
        date_from: date | None,
        date_to: date | None,
    ) -> Any:
        if date_from is not None:
            statement = statement.where(date_column >= date_from)
        if date_to is not None:
            statement = statement.where(date_column <= date_to)
        return statement

    def _apply_datetime_filters(
        self,
        statement: Any,
        datetime_column: Any,
        date_from: date | None,
        date_to: date | None,
    ) -> Any:
        if date_from is not None:
            statement = statement.where(datetime_column >= datetime.combine(date_from, time.min))
        if date_to is not None:
            statement = statement.where(datetime_column <= datetime.combine(date_to, time.max))
        return statement

    def _ratio(self, numerator: Decimal, denominator: Decimal) -> float:
        if denominator == 0:
            return 0
        return self._to_float(numerator / denominator)

    def _percentage(self, numerator: Decimal | int, denominator: Decimal | int) -> float:
        denominator_decimal = self._to_decimal(denominator)
        if denominator_decimal == 0:
            return 0
        return self._to_float((self._to_decimal(numerator) / denominator_decimal) * 100)

    def _to_decimal(self, value: Any) -> Decimal:
        return Decimal(str(value or 0))

    def _to_float(self, value: Decimal) -> float:
        return float(round(value, 2))
