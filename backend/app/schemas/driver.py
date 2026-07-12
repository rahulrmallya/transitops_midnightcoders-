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
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Sanjay Patil",
                "license_number": "TO-DL-00001",
                "license_category": "HMV",
                "license_expiry_date": "2027-09-05",
                "contact_number": "+919870011000",
                "safety_score": 92,
                "status": "AVAILABLE",
            }
        },
    )

    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=100)
    license_category: str = Field(min_length=1, max_length=50)
    license_expiry_date: date
    contact_number: str = Field(min_length=1, max_length=30)
    safety_score: float = Field(ge=0, le=100)
    status: DriverStatus


class DriverUpdate(DriverBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "contact_number": "+919870011001",
                "safety_score": 94,
                "status": "AVAILABLE",
            }
        },
    )

    name: str | None = Field(default=None, min_length=1, max_length=255)
    license_number: str | None = Field(default=None, min_length=1, max_length=100)
    license_category: str | None = Field(default=None, min_length=1, max_length=50)
    license_expiry_date: date | None = None
    contact_number: str | None = Field(default=None, min_length=1, max_length=30)
    safety_score: float | None = Field(default=None, ge=0, le=100)
    status: DriverStatus | None = None


class DriverResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Sanjay Patil",
                "license_number": "TO-DL-00001",
                "license_category": "HMV",
                "license_expiry_date": "2027-09-05",
                "contact_number": "+919870011000",
                "safety_score": 92,
                "status": "AVAILABLE",
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T09:30:00Z",
            }
        },
    )

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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 20,
                "page": 1,
                "limit": 10,
                "items": [],
            }
        }
    )

    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    items: list[DriverResponse]
