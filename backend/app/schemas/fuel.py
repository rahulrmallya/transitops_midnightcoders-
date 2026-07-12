
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FuelLogCreate(BaseModel):
    vehicle_id: int
    liters: float = Field(gt=0)
    cost: float = Field(ge=0)
    fuel_date: date


class FuelLogUpdate(BaseModel):
    vehicle_id: int | None = None
    liters: float | None = Field(default=None, gt=0)
    cost: float | None = Field(default=None, ge=0)
    fuel_date: date | None = None


class FuelLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    liters: float
    cost: float
    fuel_date: date
    created_at: datetime
    updated_at: datetime
