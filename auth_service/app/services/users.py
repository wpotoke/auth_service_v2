# ruff: noqa: E712
from datetime import UTC, datetime, timedelta

from auth_service.app.auth.security import (
    create_access_token,
    create_refresh_token,
    get_email_refresh_access_token,
)
from auth_service.app.core.config import settings
from auth_service.app.core.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
)
from auth_service.app.models.users import User as UserModel
from auth_service.app.repositories.users import UserRepository
from auth_service.app.schemas.tokens import RefreshTokenBase, TokenGroup
from auth_service.app.schemas.users import UserCreate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user(self, user_id: int) -> UserModel | None:
        user_db = await self.user_repo.get_by_id(user_id)
        if not user_db:
            raise NotFoundException(f"User with id {user_id} not found")
        return user_db

    async def get_user_by_email(self, email: str) -> UserModel | None:
        user_db = await self.user_repo.get_user_by_email(email)
        if not user_db:
            raise NotFoundException("User with this email not found")
        return user_db

    async def create_user(self, user: UserCreate) -> UserModel:
        existing_user_email = await self.user_repo.get_user_by_email(user.email)
        if existing_user_email:
            raise ConflictException("User already exists")
        user_db = await self.user_repo.create(user)
        return user_db

    async def delete_user(self, user_id: int, email) -> bool:
        user_db = self.user_repo.get_user_by_email(email=email)
        if not user_db:
            raise NotFoundException(f"User with id {user_id} not found")
        if user_db.id != user_id:
            raise BusinessException("Don't have such permission")
        return await self.user_repo.delete(user_id)

    async def authenticate_user(self, email: str, password: str) -> UserModel | None:
        authed_user = await self.user_repo.authenticate(email, password)
        if not authed_user:
            raise BusinessException("email or password wrong")
        return authed_user

    async def refresh_access_token(self, refresh_token: str) -> dict:
        email = await get_email_refresh_access_token(refresh_token=refresh_token)
        user = await self.get_user_by_email(email)
        if not user:
            raise NotFoundException("User with this email not found")
        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id})

        refresh_token_schema = RefreshTokenBase(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return TokenGroup(access_token=access_token, refresh_token=refresh_token_schema)
