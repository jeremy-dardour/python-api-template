from typing import ClassVar
from uuid import UUID

from app.todos.models import Todo, TodoStatus


class TodoRepository:
    _todos: ClassVar[list[Todo]] = [
        Todo(
            id=UUID("3f2504e0-4f89-11d3-9a0c-0305e82c3301"),
            name="Buy groceries",
            status=TodoStatus.PENDING,
        ),
        Todo(
            id=UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"),
            name="Write tests",
            status=TodoStatus.IN_PROGRESS,
        ),
        Todo(
            id=UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8"),
            name="Deploy to production",
            status=TodoStatus.COMPLETED,
        ),
    ]

    async def get_all(self) -> list[Todo]:
        return self._todos
