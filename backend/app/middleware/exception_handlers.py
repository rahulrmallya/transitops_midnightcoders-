import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.common import ErrorResponse


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(
            "HTTP exception on %s %s: %s",
            request.method,
            request.url.path,
            message,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=message, errors={}).model_dump(),
        headers=getattr(exc, "headers", None),
    )


def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.info(
        "Request validation failed on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            ErrorResponse(
                message="Validation error",
                errors={"details": exc.errors()},
            )
        ),
    )


def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.info(
        "Validation failed on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            ErrorResponse(
                message="Validation error",
                errors={"details": exc.errors()},
            )
        ),
    )


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="Internal server error",
            errors={},
        ).model_dump(),
    )
