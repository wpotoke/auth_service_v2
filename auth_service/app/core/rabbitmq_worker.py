# pylint:disable=broad-exception-caught
from typing import Optional
import asyncio
import aio_pika
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractRobustConnection,
    AbstractExchange,
)
from auth_service.app.core.config import settings
from auth_service.app.auth.security import get_email_current_user
from auth_service.app.core.database import async_session_maker
from auth_service.app.repositories.users import UserRepository
from auth_service.app.services.users import UserService

RABBITMQ_URL = settings.RABBITMQ_URL


async def process_get_user_id_by_token(
    message: AbstractIncomingMessage, default_exchange: AbstractExchange
):
    """Обрабатывает входящий RPC-запрос на получение id по access токену"""
    async with message.process():
        try:
            token = message.body.decode("utf-8")
            email = await get_email_current_user(token=token)
            async with async_session_maker() as db:
                repo = UserRepository(db=db)
                service = UserService(user_repo=repo)
                user = await service.get_user_by_email(email=email)
                user_id = str(user.id)
        except Exception as e:
            print(f"Error in during handle message: {e}")

        if message.reply_to and message.correlation_id:
            await default_exchange.publish(
                aio_pika.Message(
                    body=user_id.encode(), correlation_id=message.correlation_id
                ),
                routing_key=message.reply_to,
            )


async def run_consumer():
    """Запускает consumer'а, который слушает очередь RPC-запросов."""
    connection: Optional[AbstractRobustConnection] = None
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            default_exchange = channel.default_exchange
            queue = await channel.declare_queue("token_check_queue")
            await queue.consume(
                lambda message: process_get_user_id_by_token(message, default_exchange)
            )

            await asyncio.Future()
    except asyncio.CancelledError:
        print("Получен сигнал отмены, consumer завершает работу.")
    finally:
        if connection and not connection.is_closed:
            await connection.close()
            print("Соединение с RabbitMQ закрыто.")
