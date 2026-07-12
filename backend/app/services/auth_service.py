from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.auth.token import create_access_token
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import AuthUserResponse, LoginRequest, RegisterRequest, TokenResponse


ALLOWED_ROLES = {
    "Fleet Manager",
    "Dispatcher",
    "Safety Officer",
    "Financial Analyst",
}


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, payload: RegisterRequest) -> User:
        existing_user = self.db.scalar(select(User).where(User.email == payload.email))
        if existing_user is not None:
            raise ValueError("Email already registered")

        if payload.role not in ALLOWED_ROLES:
            raise ValueError("Invalid role")

        role = self._get_or_create_role(payload.role)
        user = User(
            full_name=payload.full_name,
            email=str(payload.email),
            hashed_password=hash_password(payload.password),
            role_id=role.id,
            is_active=True,
        )

        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception:
            self.db.rollback()
            raise
        return user

    def authenticate_user(self, payload: LoginRequest) -> TokenResponse | None:
        user = self.db.scalar(select(User).where(User.email == payload.email))
        if user is None or not verify_password(payload.password, user.hashed_password):
            return None

        access_token = create_access_token({"sub": str(user.id), "role": user.role.name})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=self.to_auth_user_response(user),
        )

    def to_auth_user_response(self, user: User) -> AuthUserResponse:
        return AuthUserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _get_or_create_role(self, role_name: str) -> Role:
        role = self.db.scalar(select(Role).where(Role.name == role_name))
        if role is not None:
            return role

        role = Role(name=role_name, description=None)
        self.db.add(role)
        self.db.flush()
        return role
