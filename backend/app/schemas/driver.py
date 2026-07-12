
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import DriverStatus


class DriverCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=100)
    license_category: str = Field(min_length=1, max_length=50)
    license_expiry_date: date
    contact_number: str = Field(min_length=1, max_length=30)
    safety_score: float = Field(ge=0, le=100)
    status: DriverStatus


class DriverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    license_number: str | None = Field(default=None, min_length=1, max_length=100)
    license_category: str | None = Field(default=None, min_length=1, max_length=50)
    license_expiry_date: date | None = None
    contact_number: str | None = Field(default=None, min_length=1, max_length=30)
    safety_score: float | None = Field(default=None, ge=0, le=100)
    status: DriverStatus | None = None


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    contact_number: str
    safety_score: float
    status: DriverStatus
    created_at: datetime
    updated_at: datetime
