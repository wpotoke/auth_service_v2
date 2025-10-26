# pylint:disable=unused-argument
from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Path, status
from fastapi_limiter.depends import RateLimiter

from task_service.app.core.dependencies import (
    get_current_user,
    get_redis_client,
    get_task_service,
)
from task_service.app.schemas.tasks import Task, TaskCreate
from task_service.app.services.tasks import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "",
    response_model=list[Task],
    dependencies=[Depends(RateLimiter(times=15, minutes=1))],
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
) -> list[Task]:
    return await task_service.get_tasks(user_id=user_id)


@router.get(
    "/{task_id}",
    response_model=Task,
    dependencies=[Depends(RateLimiter(times=10, minutes=1))],
    status_code=status.HTTP_200_OK,
)
async def get_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> Task | None:
    return await task_service.get_task_by_id(task_id=task_id, user_id=user_id, r=redis_client)


@router.post(
    "",
    response_model=Task,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    task_create: TaskCreate,
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> Task | None:
    return await task_service.create_task(task_create=task_create, user_id=user_id, r=redis_client)


@router.put(
    "/{task_id}",
    response_model=Task,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    task_update: TaskCreate,
) -> Task | None:
    return await task_service.task_update(task_id=task_id, task_update=task_update, user_id=user_id)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
):
    return await task_service.task_delete(task_id=task_id, user_id=user_id)
