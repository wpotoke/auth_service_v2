# pylint:disable=unused-argument,redefined-outer-name
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from task_service.app.core.rabbitmq import user_validator_instance
from task_service.app.api.routers.tasks import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await user_validator_instance.connect()
    yield
    await user_validator_instance.close()


app = FastAPI(
    title="FastAPI task service - сервис задач", version="0.1.0", lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)
