from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
            }
        }
    )

    success: bool = True
    message: str
    data: T


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": {
                    "details": [
                        {
                            "loc": ["body", "field_name"],
                            "msg": "Field required",
                            "type": "missing",
                        }
                    ]
                },
            }
        }
    )

    success: bool = False
    message: str
    errors: dict[str, Any] = Field(default_factory=dict)


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
