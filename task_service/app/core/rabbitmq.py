import asyncio
import uuid
from typing import Optional
import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from task_service.app.core.config import settings


RABBITMQ_URL = settings.RABBITMQ_URL


class RpcClient:
    """Асинхронный RPC клиент для RabbitMQ."""

    def __init__(self, amqp_url: str = RABBITMQ_URL):
        self.amqp_url: str = amqp_url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.callback_queue: Optional[aio_pika.Queue] = None
        self.futures = {}
        self.loop = asyncio.get_running_loop()

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url, loop=self.loop)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response, no_ack=True)

    async def close(self):
        if self.connection and not self.connection.is_closed():
            await self.connection.close()

    async def on_response(self, message: AbstractIncomingMessage):
        future = self.futures.pop(message.correlation_id, None)
        if future:
            future.set_result(int(message.body.decode()))

    async def call(self, token: str):
        if not self.connection or self.connection.is_closed:
            raise ConnectionError("RPC Client is not connected.")
        correlation_id = str(uuid.uuid4)
        future = self.loop.create_future()
        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=token.encode("utf-8"),
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key="token_check_queue",
        )
        try:
            return await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
            self.futures.pop(correlation_id, None)
            return None


class RabbitMQTokenValidator:
    def __init__(self):
        self.rpc_client = RpcClient()

    async def connect(self):
        await self.rpc_client.connect()

    async def close(self):
        await self.rpc_client.close()

    async def validate_token(self, token: str):
        response = await self.rpc_client.call(token=token)
        if not response:
            return None
        return response


user_validator_instance = RabbitMQTokenValidator()
