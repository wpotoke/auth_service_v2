from typing import Optional
from task_service.app.repositories.tasks import TaskRepository
from task_service.app.models.task import Task as TaskModel
from task_service.app.schemas.tasks import TaskCreate


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_tasks(self, user_id) -> list[TaskModel]:
        return await self.task_repository.get_all(user_id=user_id)

    async def get_task_by_id(self, task_id: int, user_id) -> Optional[TaskModel]:
        task = await self.task_repository.get_by_id(task_id=task_id, user_id=user_id)
        if not task:
            raise ValueError("...")
        return task

    async def create_task(
        self, task_create: TaskCreate, user_id
    ) -> Optional[TaskModel]:
        if task_create.user_id != user_id:
            raise ValueError(f"{user_id} not qe {task_create.user_id}")
        task = await self.task_repository.create(task_create=task_create)
        print()
        if not task:
            raise ValueError("...")
        return task

    async def task_update(
        self, task_id: int, task_update: TaskCreate, user_id
    ) -> Optional[TaskModel]:
        return await self.task_repository.update(
            task_id=task_id, task_update=task_update, user_id=user_id
        )

    async def task_delete(self, task_id: int, user_id) -> bool:
        return await self.task_repository.delete(task_id=task_id, user_id=user_id)
