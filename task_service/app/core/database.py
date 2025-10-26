from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from task_service.app.core.config import settings

DATABASE_URL = settings.POSTGRES_TASK_DB_URL

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase): ...
