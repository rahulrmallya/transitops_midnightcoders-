import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.token import verify_access_token
from app.database.database import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def _require_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(http_bearer)],
) -> None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.info("Authentication credentials missing or invalid scheme")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    _: Annotated[None, Depends(_require_bearer_token)],
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    payload = verify_access_token(token)
    if payload is None:
        logger.info("Authentication token rejected")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        logger.info("Authentication token missing subject")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError) as exc:
        logger.info("Authentication token subject invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token payload",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = db.scalar(select(User).where(User.id == user_id_int))
    if user is None:
        logger.info("Authentication user lookup failed for user_id=%s", user_id_int)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authenticated user not found",
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        logger.info("Authentication inactive account for user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return current_user


def require_roles(*roles: str) -> Callable[[User], User]:
    allowed_roles = set(roles)

    def role_dependency(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        user_role = current_user.role.name if current_user.role else None
        if user_role not in allowed_roles:
            logger.info(
                "Authentication authorization failed for user_id=%s role=%s",
                current_user.id,
                user_role,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )

        return current_user

    return role_dependency
