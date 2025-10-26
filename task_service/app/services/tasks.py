import json

import redis.asyncio as redis

from task_service.app.models.task import Task as TaskModel
from task_service.app.repositories.tasks import TaskRepository
from task_service.app.schemas.tasks import Task as TaskSchema
from task_service.app.schemas.tasks import TaskCreate


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_tasks(self, user_id: int) -> list[TaskModel]:
        return await self.task_repository.get_all(user_id=user_id)

    async def get_task_by_id(
        self, task_id: int, user_id: int, r: redis.Redis
    ) -> TaskModel | TaskSchema | None:
        cache_key = f"task:{task_id}-user:{user_id}"
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            return TaskSchema.model_validate_json(data)
        task_model = await self.task_repository.get_by_id(task_id=task_id, user_id=user_id)
        if not task_model:
            raise ValueError("...")
        task_schema = TaskSchema.model_validate(task_model)
        task_json = json.dumps(task_schema.model_dump_json())
        await r.setex(name=cache_key, value=task_json, time=60)
        return task_model

    async def create_task(self, task_create: TaskCreate, user_id: int, r: redis.Redis) -> TaskModel | None:
        if task_create.user_id != user_id:
            raise ValueError(f"{user_id} not qe {user_id}")
        task = await self.task_repository.create(task_create=task_create)
        if not task:
            raise ValueError("...")
        cache_key = f"task:{task.id}-user:{user_id}"
        await r.delete(cache_key)
        return task

    async def task_update(self, task_id: int, task_update: TaskCreate, user_id: int) -> TaskModel | None:
        return await self.task_repository.update(task_id=task_id, task_update=task_update, user_id=user_id)

    async def task_delete(self, task_id: int, user_id) -> bool:
        return await self.task_repository.delete(task_id=task_id, user_id=user_id)
