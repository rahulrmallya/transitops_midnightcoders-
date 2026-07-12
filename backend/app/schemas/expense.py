
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    vehicle_id: int
    expense_type: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    expense_date: date
    description: str | None = None


class ExpenseUpdate(BaseModel):
    vehicle_id: int | None = None
    expense_type: str | None = Field(default=None, min_length=1, max_length=100)
    amount: float | None = Field(default=None, gt=0)
    expense_date: date | None = None
    description: str | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    expense_type: str
    amount: float
    expense_date: date
    description: str | None
    created_at: datetime
    updated_at: datetime
