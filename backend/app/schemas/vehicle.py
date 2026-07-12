
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import VehicleStatus


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=1, max_length=100)
    vehicle_name: str = Field(min_length=1, max_length=255)
    vehicle_type: str = Field(min_length=1, max_length=100)
    max_load_capacity: float = Field(gt=0)
    odometer: float = Field(ge=0)
    acquisition_cost: float = Field(ge=0)
    status: VehicleStatus


class VehicleUpdate(BaseModel):
    registration_number: str | None = Field(default=None, min_length=1, max_length=100)
    vehicle_name: str | None = Field(default=None, min_length=1, max_length=255)
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=100)
    max_load_capacity: float | None = Field(default=None, gt=0)
    odometer: float | None = Field(default=None, ge=0)
    acquisition_cost: float | None = Field(default=None, ge=0)
    status: VehicleStatus | None = None


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registration_number: str
    vehicle_name: str
    vehicle_type: str
    max_load_capacity: float
    odometer: float
    acquisition_cost: float
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime
