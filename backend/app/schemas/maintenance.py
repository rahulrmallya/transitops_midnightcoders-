
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceLogCreate(BaseModel):
    vehicle_id: int
    maintenance_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    cost: float = Field(ge=0)
    start_date: date
    end_date: date
    status: str = Field(min_length=1, max_length=50)


class MaintenanceLogUpdate(BaseModel):
    vehicle_id: int | None = None
    maintenance_type: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    cost: float | None = Field(default=None, ge=0)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)


class MaintenanceLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    maintenance_type: str
    description: str | None
    cost: float
    start_date: date
    end_date: date
    status: str
    created_at: datetime
    updated_at: datetime
