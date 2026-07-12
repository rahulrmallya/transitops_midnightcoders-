from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class FuelLogCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": 1,
                "liters": 82.5,
                "cost": 7788.75,
                "fuel_date": "2026-07-12",
            }
        }
    )

    vehicle_id: int = Field(gt=0)
    liters: float = Field(gt=0)
    cost: float = Field(ge=0)
    fuel_date: date


class FuelLogUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "liters": 84,
                "cost": 7938,
                "fuel_date": "2026-07-12",
            }
        }
    )

    vehicle_id: int | None = Field(default=None, gt=0)
    liters: float | None = Field(default=None, gt=0)
    cost: float | None = Field(default=None, ge=0)
    fuel_date: date | None = None


class FuelLogResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "vehicle_id": 1,
                "liters": 82.5,
                "cost": 7788.75,
                "fuel_date": "2026-07-12",
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T09:30:00Z",
            }
        },
    )

    id: int
    vehicle_id: int
    liters: float
    cost: float
    fuel_date: date
    created_at: datetime
    updated_at: datetime
