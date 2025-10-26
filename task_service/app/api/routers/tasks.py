# pylint:disable=unused-argument
from typing import Annotated, Optional
import redis.asyncio as redis
from fastapi import APIRouter, Depends, Path, status, Request
from task_service.app.core.dependencies import (
    get_task_service,
    get_current_user,
    get_redis_client,
)
from task_service.app.services.tasks import TaskService
from task_service.app.schemas.tasks import Task, TaskCreate
from task_service.app.core.limiter import limiter


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task], status_code=status.HTTP_200_OK)
@limiter.limit("15/min")
async def get_tasks(
    request: Request,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
) -> list[Task]:
    return await task_service.get_tasks(user_id=user_id)


@router.get("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
@limiter.limit("15/min")
async def get_task(
    request: Request,
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> Optional[Task]:
    return await task_service.get_task_by_id(
        task_id=task_id, user_id=user_id, r=redis_client
    )


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/min")
async def create_task(
    request: Request,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    task_create: TaskCreate,
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)],
) -> Optional[Task]:
    return await task_service.create_task(
        task_create=task_create, user_id=user_id, r=redis_client
    )


@router.put("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
@limiter.limit("5/min")
async def update_task(
    request: Request,
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    task_update: TaskCreate,
) -> Optional[Task]:
    return await task_service.task_update(
        task_id=task_id, task_update=task_update, user_id=user_id
    )


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
):
    return await task_service.task_delete(task_id=task_id, user_id=user_id)
