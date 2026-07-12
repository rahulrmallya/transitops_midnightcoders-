from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import IdMixin, TimestampMixin


class FuelLog(IdMixin, TimestampMixin, Base):
    __tablename__ = "fuel_logs"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    liters: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fuel_date: Mapped[Date] = mapped_column(Date, nullable=False)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="fuel_logs")