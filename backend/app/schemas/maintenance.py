from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MaintenanceLogCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "vehicle_id": 4,
                "maintenance_type": "Brake Inspection",
                "description": "Front axle brake inspection before long-haul dispatch.",
                "cost": 18500,
                "start_date": "2026-07-12",
                "end_date": "2026-07-14",
                "status": "OPEN",
            }
        }
    )

    vehicle_id: int = Field(gt=0)
    maintenance_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    cost: float = Field(ge=0)
    start_date: date
    end_date: date
    status: str = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_date_range(self) -> "MaintenanceLogCreate":
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date")
        return self


class MaintenanceLogUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Brake pads replaced and road test completed.",
                "cost": 21200,
                "status": "CLOSED",
            }
        }
    )

    vehicle_id: int | None = Field(default=None, gt=0)
    maintenance_type: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    cost: float | None = Field(default=None, ge=0)
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_date_range(self) -> "MaintenanceLogUpdate":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError("End date must be on or after start date")
        return self


class MaintenanceLogResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "vehicle_id": 4,
                "maintenance_type": "Brake Inspection",
                "description": "Front axle brake inspection before long-haul dispatch.",
                "cost": 18500,
                "start_date": "2026-07-12",
                "end_date": "2026-07-14",
                "status": "OPEN",
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T09:30:00Z",
            }
        },
    )

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
