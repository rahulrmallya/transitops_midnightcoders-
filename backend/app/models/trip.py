from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import TripStatus


class Trip(IdMixin, TimestampMixin, Base):
    __tablename__ = "trips"

    trip_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo_weight: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    planned_distance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    actual_distance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fuel_consumed: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    status: Mapped[TripStatus] = mapped_column(
        SAEnum(TripStatus, name="trip_status", native_enum=False),
        nullable=False,
    )

    vehicle: Mapped["Vehicle"] = relationship(back_populates="trips")
    driver: Mapped["Driver"] = relationship(back_populates="trips")