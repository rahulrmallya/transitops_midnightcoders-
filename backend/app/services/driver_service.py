from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.models.enums import DriverStatus
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
        statement = select(Driver)
        count_statement = select(func.count()).select_from(Driver)

        filters = []
        if status_filter is not None:
            filters.append(Driver.status == status_filter)
        if license_type:
            filters.append(Driver.license_category == license_type)
        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Driver.name.ilike(search_pattern),
                    Driver.license_number.ilike(search_pattern),
                )
            )

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

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
