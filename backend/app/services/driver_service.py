<<<<<<< HEAD
from datetime import date
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
=======
from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.enums import DriverStatus
<<<<<<< HEAD
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

=======
from app.schemas.driver import DriverCreate, DriverListResponse, DriverResponse, DriverUpdate


class DriverService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_drivers(
        self,
        *,
        status_filter: DriverStatus | None,
        license_type: str | None,
        search: str | None,
        sort_by: str,
        sort_order: str,
        page: int,
        limit: int,
    ) -> DriverListResponse:
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
        statement = select(Driver)
        count_statement = select(func.count()).select_from(Driver)

        filters = []
<<<<<<< HEAD
        if status is not None:
            filters.append(Driver.status == status)
        if license_category:
            filters.append(Driver.license_category == license_category)
        if search:
            search_pattern = f"%{search}%"
=======
        if status_filter is not None:
            filters.append(Driver.status == status_filter)
        if license_type:
            filters.append(Driver.license_category == license_type)
        if search:
            search_pattern = f"%{search.strip()}%"
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
            filters.append(
                or_(
                    Driver.name.ilike(search_pattern),
                    Driver.license_number.ilike(search_pattern),
                )
            )

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

<<<<<<< HEAD
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
=======
        sort_columns = {
            "driver_name": Driver.name,
            "license_number": Driver.license_number,
            "created_at": Driver.created_at,
        }
        sort_column = sort_columns[sort_by]
        ordering = asc(sort_column) if sort_order == "asc" else desc(sort_column)
        drivers = self.db.scalars(
            statement.order_by(ordering).offset((page - 1) * limit).limit(limit)
        ).all()
        total = self.db.scalar(count_statement) or 0

        return DriverListResponse(
            total=total,
            page=page,
            limit=limit,
            items=[DriverResponse.model_validate(driver) for driver in drivers],
        )

    def get_driver(self, driver_id: int) -> DriverResponse:
        return DriverResponse.model_validate(self._get_driver(driver_id))

    def create_driver(self, payload: DriverCreate) -> DriverResponse:
        self._ensure_license_number_available(payload.license_number)
        driver = Driver(**payload.model_dump())
        self.db.add(driver)
        self._commit_or_raise_conflict()
        self.db.refresh(driver)
        return DriverResponse.model_validate(driver)

    def update_driver(self, driver_id: int, payload: DriverUpdate) -> DriverResponse:
        driver = self._get_driver(driver_id)
        changes = payload.model_dump(exclude_unset=True)
        license_number = changes.get("license_number")
        if license_number is not None and license_number != driver.license_number:
            self._ensure_license_number_available(license_number)

        for field, value in changes.items():
            setattr(driver, field, value)

        self._commit_or_raise_conflict()
        self.db.refresh(driver)
        return DriverResponse.model_validate(driver)

    def delete_driver(self, driver_id: int) -> None:
        driver = self._get_driver(driver_id)
        self.db.delete(driver)
        self.db.commit()

    def _get_driver(self, driver_id: int) -> Driver:
        driver = self.db.get(Driver, driver_id)
        if driver is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
        return driver

    def _ensure_license_number_available(self, license_number: str) -> None:
        existing_driver = self.db.scalar(
            select(Driver).where(Driver.license_number == license_number)
        )
        if existing_driver is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="License number already exists",
            )

    def _commit_or_raise_conflict(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Driver conflicts with an existing record",
            ) from exc
>>>>>>> dc05ff8cd59cb79525c7af877cfdad74a3bcd218
