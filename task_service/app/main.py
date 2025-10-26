# pylint:disable=unused-argument,redefined-outer-name,global-statement,duplicate-code
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from task_service.app.api.routers.tasks import router as task_router
from task_service.app.core.limiter import limiter
from task_service.app.core.rabbitmq import user_validator_instance
from task_service.app.core.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    await user_validator_instance.connect()
    yield
    await redis_client.close()
    await user_validator_instance.close()


app = FastAPI(title="FastAPI task service - сервис задач", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)
