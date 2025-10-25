from typing import Optional
import redis.asyncio as redis


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = redis.Redis(
            host="127.0.0.1", port=6379, db=0, decode_responses=True
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
