from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.app.core.dependencies import get_async_db
from auth_service.app.repositories.users import UserRepository
from auth_service.app.services.users import UserService


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db=db)


def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(user_repo=UserRepository(db=db))
