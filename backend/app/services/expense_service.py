from decimal import Decimal
from typing import Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.fuel_log import FuelLog
from app.models.maintenance_log import MaintenanceLog
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.vehicle_service import VehicleService


class ExpenseNotFoundError(Exception):
    pass


class ExpenseValidationError(Exception):
    pass


class ExpenseService:
    sortable_fields = {
        "expense_date": Expense.expense_date,
        "expense_type": Expense.expense_type,
        "amount": Expense.amount,
        "created_at": Expense.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db
        self.vehicle_service = VehicleService(db)

    def create_expense(self, payload: ExpenseCreate) -> Expense:
        self._validate_expense_data(payload.model_dump())
        self.vehicle_service.get_vehicle_by_id(payload.vehicle_id)

        expense = Expense(**payload.model_dump())
        self.db.add(expense)
        try:
            self.db.commit()
            self.db.refresh(expense)
        except Exception:
            self.db.rollback()
            raise
        return expense

    def get_expense_by_id(self, expense_id: int) -> Expense:
        expense = self.db.get(Expense, expense_id)
        if expense is None:
            raise ExpenseNotFoundError("Expense not found")

        return expense

    def get_all_expenses(
        self,
        *,
        vehicle_id: int | None = None,
        expense_type: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise ExpenseValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise ExpenseValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise ExpenseValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise ExpenseValidationError("Invalid sort order")

        statement = select(Expense)
        count_statement = select(func.count()).select_from(Expense)

        filters = []
        if vehicle_id is not None:
            filters.append(Expense.vehicle_id == vehicle_id)
        if expense_type:
            filters.append(Expense.expense_type == expense_type)

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        expenses = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [ExpenseResponse.model_validate(expense) for expense in expenses],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def update_expense(self, expense_id: int, payload: ExpenseUpdate) -> Expense:
        expense = self.get_expense_by_id(expense_id)
        update_data = payload.model_dump(exclude_unset=True)
        self._validate_expense_data(update_data)

        if update_data.get("vehicle_id") is not None:
            self.vehicle_service.get_vehicle_by_id(update_data["vehicle_id"])

        for field, value in update_data.items():
            setattr(expense, field, value)

        try:
            self.db.commit()
            self.db.refresh(expense)
        except Exception:
            self.db.rollback()
            raise
        return expense

    def delete_expense(self, expense_id: int) -> None:
        expense = self.get_expense_by_id(expense_id)
        self.db.delete(expense)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def calculate_vehicle_operational_cost(self, vehicle_id: int) -> Decimal:
        return calculate_vehicle_operational_cost(self.db, vehicle_id)

    def _validate_expense_data(self, data: dict[str, Any]) -> None:
        if "vehicle_id" in data and data["vehicle_id"] is None:
            raise ExpenseValidationError("Vehicle cannot be null")
        if "expense_type" in data and data["expense_type"] is None:
            raise ExpenseValidationError("Expense type cannot be null")
        if "amount" in data and data["amount"] is None:
            raise ExpenseValidationError("Amount cannot be null")
        if "amount" in data and data["amount"] <= 0:
            raise ExpenseValidationError("Amount must be greater than 0")


def calculate_vehicle_operational_cost(db: Session, vehicle_id: int) -> Decimal:
    VehicleService(db).get_vehicle_by_id(vehicle_id)

    fuel_cost = db.scalar(
        select(func.coalesce(func.sum(FuelLog.cost), 0)).where(
            FuelLog.vehicle_id == vehicle_id
        )
    )
    maintenance_cost = db.scalar(
        select(func.coalesce(func.sum(MaintenanceLog.cost), 0)).where(
            MaintenanceLog.vehicle_id == vehicle_id
        )
    )
    other_expenses = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.vehicle_id == vehicle_id
        )
    )

    return (
        Decimal(str(fuel_cost or 0))
        + Decimal(str(maintenance_cost or 0))
        + Decimal(str(other_expenses or 0))
    )
