from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.repositories.users import UserRepository
from app.services.users import UserService

from app.core.dependencies import get_async_db


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db=db)


def get_user_service(db: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(user_repo=UserRepository(db=db))
