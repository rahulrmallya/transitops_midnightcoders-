
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TripStatus


class TripCreate(BaseModel):
    trip_code: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    cargo_weight: float = Field(gt=0)
    planned_distance: float = Field(gt=0)
    actual_distance: float | None = Field(default=None, ge=0)
    fuel_consumed: float | None = Field(default=None, ge=0)
    revenue: float = Field(ge=0)
    vehicle_id: int
    driver_id: int
    status: TripStatus


class TripUpdate(BaseModel):
    trip_code: str | None = Field(default=None, min_length=1, max_length=100)
    source: str | None = Field(default=None, min_length=1, max_length=255)
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    cargo_weight: float | None = Field(default=None, gt=0)
    planned_distance: float | None = Field(default=None, gt=0)
    actual_distance: float | None = Field(default=None, ge=0)
    fuel_consumed: float | None = Field(default=None, ge=0)
    revenue: float | None = Field(default=None, ge=0)
    vehicle_id: int | None = None
    driver_id: int | None = None
    status: TripStatus | None = None


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_code: str
    source: str
    destination: str
    cargo_weight: float
    planned_distance: float
    actual_distance: float | None
    fuel_consumed: float | None
    revenue: float
    vehicle_id: int
    driver_id: int
    status: TripStatus
    created_at: datetime
    updated_at: datetime
