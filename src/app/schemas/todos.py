# src/app/schemas/todo.py
from uuid import UUID

from pydantic import BaseModel

from app.models.todos import TodoStatus


class TodoBase(BaseModel):
    id: UUID
    name: str
    status: TodoStatus


class TodoRead(TodoBase):
    pass
