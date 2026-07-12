from sqlalchemy import Enum as SAEnum
from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import IdMixin, TimestampMixin
from app.models.enums import DriverStatus


class Driver(IdMixin, TimestampMixin, Base):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    license_category: Mapped[str] = mapped_column(String(50), nullable=False)
    license_expiry_date: Mapped[Date] = mapped_column(Date, nullable=False)
    contact_number: Mapped[str] = mapped_column(String(30), nullable=False)
    safety_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[DriverStatus] = mapped_column(
        SAEnum(DriverStatus, name="driver_status", native_enum=False),
        nullable=False,
    )

    trips: Mapped[list["Trip"]] = relationship(back_populates="driver")