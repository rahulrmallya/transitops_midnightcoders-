
from datetime import date, datetime
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import DriverStatus


PHONE_NUMBER_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")


class DriverBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("contact_number", check_fields=False)
    @classmethod
    def validate_contact_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized_value = re.sub(r"[\s().-]", "", value)
        if not PHONE_NUMBER_PATTERN.fullmatch(normalized_value):
            raise ValueError("Contact number must be a valid international phone number")
        return normalized_value

    @field_validator("license_expiry_date", check_fields=False)
    @classmethod
    def validate_license_expiry_date(cls, value: date | None) -> date | None:
        if value is None:
            return value
        if value <= date.today():
            raise ValueError("License expiry date must be in the future")
        return value


class DriverCreate(DriverBase):
    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=100)
    license_category: str = Field(min_length=1, max_length=50)
    license_expiry_date: date
    contact_number: str = Field(min_length=1, max_length=30)
    safety_score: float = Field(ge=0, le=100)
    status: DriverStatus


class DriverUpdate(DriverBase):
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


class DriverListResponse(BaseModel):
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    items: list[DriverResponse]
