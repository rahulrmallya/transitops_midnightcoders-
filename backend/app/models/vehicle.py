from sqlalchemy import Enum as SAEnum
from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import VehicleStatus


class Vehicle(IdMixin, TimestampMixin, Base):
    __tablename__ = "vehicles"

    registration_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    vehicle_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(100), nullable=False)
    max_load_capacity: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    odometer: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    acquisition_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(
        SAEnum(VehicleStatus, name="vehicle_status", native_enum=False),
        nullable=False,
    )

    trips: Mapped[list["Trip"]] = relationship(back_populates="vehicle")
    fuel_logs: Mapped[list["FuelLog"]] = relationship(back_populates="vehicle")
    maintenance_logs: Mapped[list["MaintenanceLog"]] = relationship(back_populates="vehicle")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="vehicle")