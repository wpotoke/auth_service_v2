# pylint:disable=unused-argument,redefined-outer-name
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from auth_service.app.api.routers.users import router as user_router
from auth_service.app.core.rabbitmq_worker import run_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer_task = asyncio.create_task(run_consumer())
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Consumer RabbitMQ успешно остановлен.")


app = FastAPI(
    title="FastAPI user service - сервис аунтификации",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.get("/")
async def read_index():
    # Возвращаем главную HTML страницу
    return FileResponse("index.html")
