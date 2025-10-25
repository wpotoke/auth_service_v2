from typing import AsyncGenerator
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from task_service.app.core.database import async_session_maker
from task_service.app.core.rabbitmq import (
    RabbitMQTokenValidator,
    user_validator_instance,
)
from task_service.app.repositories.tasks import TaskRepository
from task_service.app.services.tasks import TaskService
from task_service.app.core.redis_client import redis_client, redis

security = HTTPBearer()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session


def get_task_repository(db: AsyncSession = Depends(get_async_db)) -> TaskRepository:
    return TaskRepository(db=db)


def get_token_validator() -> RabbitMQTokenValidator:
    return user_validator_instance


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    rabbitmq_client: RabbitMQTokenValidator = Depends(get_token_validator),
):
    """Зависимость для получения текущего пользователя"""
    user_id = await rabbitmq_client.validate_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


def get_task_service(task_repo: TaskRepository = Depends(get_task_repository)):
    return TaskService(task_repository=task_repo)


async def get_redis_client() -> redis.Redis:
    if not redis_client.client:
        await redis_client.connect()
    return redis_client.client
