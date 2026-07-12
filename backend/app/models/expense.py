from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.base import IdMixin, TimestampMixin


class Expense(IdMixin, TimestampMixin, Base):
    __tablename__ = "expenses"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    expense_type: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    expense_date: Mapped[Date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="expenses")