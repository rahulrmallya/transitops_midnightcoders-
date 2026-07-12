from datetime import date
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.enums import DriverStatus
from app.schemas.driver import DriverCreate, DriverResponse, DriverUpdate


class DriverNotFoundError(Exception):
    pass


class DriverDuplicateError(Exception):
    pass


class DriverValidationError(Exception):
    pass


class DriverService:
    sortable_fields = {
        "name": Driver.name,
        "license_expiry_date": Driver.license_expiry_date,
        "safety_score": Driver.safety_score,
        "created_at": Driver.created_at,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_driver(self, payload: DriverCreate) -> Driver:
        data = payload.model_dump()
        self._validate_driver_data(data, validate_expiry_date=True)
        self._ensure_license_number_unique(payload.license_number)
        self._ensure_contact_number_unique(payload.contact_number)

        driver = Driver(**data)
        self.db.add(driver)
        self.db.commit()
        self.db.refresh(driver)
        return driver

    def get_driver_by_id(self, driver_id: int) -> Driver:
        driver = self.db.get(Driver, driver_id)
        if driver is None:
            raise DriverNotFoundError("Driver not found")

        return driver

    def get_all_drivers(
        self,
        *,
        status: DriverStatus | None = None,
        license_category: str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        if page < 1:
            raise DriverValidationError("Page must be greater than or equal to 1")
        if limit < 1:
            raise DriverValidationError("Limit must be greater than or equal to 1")
        if sort_by not in self.sortable_fields:
            raise DriverValidationError("Invalid sort field")
        if sort_order not in {"asc", "desc"}:
            raise DriverValidationError("Invalid sort order")

        statement = select(Driver)
        count_statement = select(func.count()).select_from(Driver)

        filters = []
        if status is not None:
            filters.append(Driver.status == status)
        if license_category:
            filters.append(Driver.license_category == license_category)
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Driver.name.ilike(search_pattern),
                    Driver.license_number.ilike(search_pattern),
                )
            )

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        sort_column = self.sortable_fields[sort_by]
        sort_expression = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        offset = (page - 1) * limit

        drivers = self.db.scalars(
            statement.order_by(sort_expression).offset(offset).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return {
            "items": [DriverResponse.model_validate(driver) for driver in drivers],
            "page": page,
            "limit": limit,
            "total": total,
        }

    def update_driver(self, driver_id: int, payload: DriverUpdate) -> Driver:
        driver = self.get_driver_by_id(driver_id)
        update_data = payload.model_dump(exclude_unset=True)
        self._validate_driver_data(update_data, validate_expiry_date=True)

        license_number = update_data.get("license_number")
        if license_number is not None:
            self._ensure_license_number_unique(license_number, driver_id)

        contact_number = update_data.get("contact_number")
        if contact_number is not None:
            self._ensure_contact_number_unique(contact_number, driver_id)

        for field, value in update_data.items():
            setattr(driver, field, value)

        self.db.commit()
        self.db.refresh(driver)
        return driver

    def delete_driver(self, driver_id: int) -> None:
        driver = self.get_driver_by_id(driver_id)
        self.db.delete(driver)
        self.db.commit()

    def _ensure_license_number_unique(
        self,
        license_number: str,
        driver_id: int | None = None,
    ) -> None:
        statement = select(Driver).where(Driver.license_number == license_number)
        if driver_id is not None:
            statement = statement.where(Driver.id != driver_id)

        existing_driver = self.db.scalar(statement)
        if existing_driver is not None:
            raise DriverDuplicateError("License number already exists")

    def _ensure_contact_number_unique(
        self,
        contact_number: str,
        driver_id: int | None = None,
    ) -> None:
        statement = select(Driver).where(Driver.contact_number == contact_number)
        if driver_id is not None:
            statement = statement.where(Driver.id != driver_id)

        existing_driver = self.db.scalar(statement)
        if existing_driver is not None:
            raise DriverDuplicateError("Contact number already exists")

    def _validate_driver_data(
        self,
        data: dict[str, Any],
        *,
        validate_expiry_date: bool,
    ) -> None:
        if "status" in data and data["status"] not in set(DriverStatus):
            raise DriverValidationError("Invalid driver status")
        if "safety_score" in data and not 0 <= data["safety_score"] <= 100:
            raise DriverValidationError("Safety score must be between 0 and 100")
        if (
            validate_expiry_date
            and "license_expiry_date" in data
            and data["license_expiry_date"] < date.today()
        ):
            raise DriverValidationError("License expiry date must not be in the past")
