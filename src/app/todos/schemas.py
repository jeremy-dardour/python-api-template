from uuid import UUID

from pydantic import BaseModel

from app.todos.models import TodoStatus


class TodoBase(BaseModel):
    id: UUID
    name: str
    status: TodoStatus


class TodoRead(TodoBase):
    pass
