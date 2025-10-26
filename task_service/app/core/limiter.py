from fastapi_limiter import FastAPILimiter

from .redis_client import redis_client


async def init_limiter():
    """
    Инициализация FastAPI Limiter с существующим Redis клиентом
    """
    if not redis_client.client:
        await redis_client.connect()
    await FastAPILimiter.init(redis_client.client)
