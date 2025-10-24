from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status
from task_service.app.core.dependencies import get_task_service, get_current_user
from task_service.app.services.tasks import TaskService
from task_service.app.schemas.tasks import Task, TaskCreate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task], status_code=status.HTTP_200_OK)
async def get_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
) -> list[Task]:
    return await task_service.get_tasks(user_id=user_id)


@router.get("/{task_id}", response_model=list[Task], status_code=status.HTTP_200_OK)
async def get_task(
    task_id: Annotated[int, Path(ge=1)],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
) -> Optional[Task]:
    return await task_service.get_task_by_id(task_id=task_id, user_id=user_id)


@router.post("", response_model=Optional[Task], status_code=status.HTTP_201_CREATED)
async def create_task(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    user_id: Annotated[int, Depends(get_current_user)],
    task_create: TaskCreate,
) -> Optional[Task]:
    return await task_service.create_task(task_create=task_create, user_id=user_id)


@router.put("/{task_id}", response_model=Task, status_code=status.HTTP_200_OK)
async def update_task(
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
