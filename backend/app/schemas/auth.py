from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Neha Kapoor",
                "email": "dispatcher@transitops.local",
                "password": "TransitOps@123",
                "role": "Dispatcher",
            }
        }
    )

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "dispatcher@transitops.local",
                "password": "TransitOps@123",
            }
        }
    )

    email: EmailStr
    password: str = Field(min_length=8)


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "full_name": "Neha Kapoor",
                "email": "dispatcher@transitops.local",
                "role": "Dispatcher",
                "is_active": True,
                "created_at": "2026-07-12T09:30:00Z",
                "updated_at": "2026-07-12T09:30:00Z",
            }
        },
    )

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 2,
                    "full_name": "Neha Kapoor",
                    "email": "dispatcher@transitops.local",
                    "role": "Dispatcher",
                    "is_active": True,
                    "created_at": "2026-07-12T09:30:00Z",
                    "updated_at": "2026-07-12T09:30:00Z",
                },
            }
        }
    )

    access_token: str
    token_type: str
    user: AuthUserResponse
