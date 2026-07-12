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


@router.post(
    "/register",
    response_model=SuccessResponse[AuthUserResponse],
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse[AuthUserResponse]:
    service = AuthService(db)
    try:
        user = service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return SuccessResponse(
        message="Registration successful",
        data=service.to_auth_user_response(user),
    )


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SuccessResponse[TokenResponse]:
    service = AuthService(db)
    auth_data = service.authenticate_user(payload)
    if auth_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return SuccessResponse(message="Login successful", data=auth_data)


@router.get(
    "/me",
    response_model=SuccessResponse[AuthUserResponse],
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
