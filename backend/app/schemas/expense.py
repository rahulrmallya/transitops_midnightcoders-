from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": 1,
                "expense_type": "Toll",
                "amount": 1250,
                "expense_date": "2026-07-12",
                "description": "Mumbai-Pune expressway toll charges.",
            }
        }
    )

    vehicle_id: int = Field(gt=0)
    expense_type: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    expense_date: date
    description: str | None = None


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 1325,
                "description": "Updated toll receipt amount.",
            }
        }
    )

    vehicle_id: int | None = Field(default=None, gt=0)
    expense_type: str | None = Field(default=None, min_length=1, max_length=100)
    amount: float | None = Field(default=None, gt=0)
    expense_date: date | None = None
    description: str | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "vehicle_id": 1,
                "expense_type": "Toll",
                "amount": 1250,
                "expense_date": "2026-07-12",
                "description": "Mumbai-Pune expressway toll charges.",
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T09:30:00Z",
            }
        },
    )

    id: int
    vehicle_id: int
    expense_type: str
    amount: float
    expense_date: date
    description: str | None
    created_at: datetime
    updated_at: datetime
