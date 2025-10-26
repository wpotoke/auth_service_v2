import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from task_service.app.models.task import TaskStatus


class TaskCreate(BaseModel):
    name: Annotated[str, Field(min_length=3, max_length=50, description="Название задачи")]
    status: TaskStatus
    description: Annotated[
        str | None,
        Field(default=None, max_length=20000, description="Описание задачи"),
    ]
    user_id: Annotated[int, Field(...)]

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if not value.strip():
            raise ValueError("Value cannot be empty or whitespace only")
        return value.strip()


class Task(BaseModel):
    id: Annotated[int, Field(description="Индификатор задачи")]
    name: str
    status: TaskStatus
    description: str
    user_id: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
