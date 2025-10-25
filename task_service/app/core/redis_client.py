import os
from typing import Optional
import redis.asyncio as redis


REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_HOST = os.getenv("REDIS_HOST")


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )
        try:
            await self.client.ping()
            print("Успешное подключение")
        except redis.ConnectionError() as e:
            print(f"Не удалось подключиться к Redis: {e}")
            self.client = None

    async def close(self):
        if self.client:
            await self.client.close()


redis_client = RedisClient()
