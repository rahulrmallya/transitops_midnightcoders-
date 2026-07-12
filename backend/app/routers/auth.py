import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=SuccessResponse[AuthUserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Creates a user account with one of the supported TransitOps roles.",
    responses={
        status.HTTP_201_CREATED: {"description": "Registration successful."},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid registration request."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error."},
    },
)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse[AuthUserResponse]:
    service = AuthService(db)
    try:
        user = service.register_user(payload)
    except ValueError as exc:
        logger.info("Authentication registration failed for email=%s: %s", payload.email, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    logger.info("Authentication registration successful for user_id=%s", user.id)
    return SuccessResponse(
        message="Registration successful",
        data=service.to_auth_user_response(user),
    )


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="Authenticate user",
    description="Validates user credentials and returns a bearer access token.",
    responses={
        status.HTTP_200_OK: {"description": "Login successful."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error."},
    },
)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse[TokenResponse]:
    service = AuthService(db)
    auth_data = service.authenticate_user(payload)
    if auth_data is None:
        logger.info("Authentication login failed for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Authentication login successful for email=%s", payload.email)
    return SuccessResponse(message="Login successful", data=auth_data)


@router.get(
    "/me",
    response_model=SuccessResponse[AuthUserResponse],
    summary="Get authenticated profile",
    description="Returns the active authenticated user's profile and role.",
    responses={
        status.HTTP_200_OK: {"description": "User profile retrieved."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required."},
        status.HTTP_404_NOT_FOUND: {"description": "Authenticated user not found."},
    },
)
def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse[AuthUserResponse]:
    service = AuthService(db)
    return SuccessResponse(
        message="User profile retrieved",
        data=service.to_auth_user_response(current_user),
    )
