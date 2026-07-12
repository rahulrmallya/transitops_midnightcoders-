from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TripStatus


class TripCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trip_code": "TO-TRIP-0101",
                "source": "Mumbai",
                "destination": "Pune",
                "cargo_weight": 12500,
                "planned_distance": 148,
                "vehicle_id": 1,
                "driver_id": 1,
                "status": "DRAFT",
            }
        }
    )

    trip_code: str = Field(min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=255)
    destination: str = Field(min_length=1, max_length=255)
    cargo_weight: float = Field(gt=0)
    planned_distance: float = Field(gt=0)
    actual_distance: float | None = Field(default=None, ge=0)
    fuel_consumed: float | None = Field(default=None, ge=0)
    revenue: float = Field(default=0, ge=0)
    vehicle_id: int = Field(gt=0)
    driver_id: int = Field(gt=0)
    status: TripStatus | None = None


class TripUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "destination": "Nashik",
                "cargo_weight": 11800,
                "planned_distance": 167,
                "vehicle_id": 3,
                "driver_id": 5,
            }
        }
    )

    trip_code: str | None = Field(default=None, min_length=1, max_length=100)
    source: str | None = Field(default=None, min_length=1, max_length=255)
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    cargo_weight: float | None = Field(default=None, gt=0)
    planned_distance: float | None = Field(default=None, gt=0)
    actual_distance: float | None = Field(default=None, ge=0)
    fuel_consumed: float | None = Field(default=None, ge=0)
    revenue: float | None = Field(default=None, ge=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    driver_id: int | None = Field(default=None, gt=0)
    status: TripStatus | None = None


class TripComplete(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actual_distance": 152,
                "fuel_consumed": 32.5,
                "revenue": 14500,
            }
        }
    )

    actual_distance: float = Field(gt=0)
    fuel_consumed: float = Field(ge=0)
    revenue: float = Field(ge=0)


class TripResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "trip_code": "TO-TRIP-0101",
                "source": "Mumbai",
                "destination": "Pune",
                "cargo_weight": 12500,
                "planned_distance": 148,
                "actual_distance": 152,
                "fuel_consumed": 32.5,
                "revenue": 14500,
                "vehicle_id": 1,
                "driver_id": 1,
                "status": "COMPLETED",
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T12:45:00Z",
            }
        },
    )

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
