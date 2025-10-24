from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from task_service.app.models.task import Task as TaskModel
from task_service.app.schemas.tasks import TaskCreate


class TaskRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id) -> list[TaskModel]:
        result = await self.db.scalars(
            select(TaskModel).where(
                TaskModel.is_active == True, TaskModel.user_id == user_id
            )
        )
        tasks = result.all()
        return tasks

    async def get_by_id(self, task_id: int, user_id) -> Optional[TaskModel]:
        result = await self.db.scalars(
            select(TaskModel).where(
                TaskModel.id == task_id,
                TaskModel.is_active == True,
                TaskModel.user_id == user_id,
            )
        )
        task = result.first()
        return task

    async def create(self, task_create: TaskCreate):

        task = TaskModel(**task_create.model_dump())
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: int, task_update: TaskCreate, user_id):
        result = await self.db.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id, TaskModel.user_id == user_id)
            .values(**task_update.model_dump())
        )
        await self.db.commit()
        if result.rowcount > 0:
            return await self.get_by_id(task_id=task_id, user_id=user_id)
        return None

    async def delete(self, task_id: int, user_id) -> bool:
        result = await self.db.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id, TaskModel.user_id == user_id)
            .values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0
