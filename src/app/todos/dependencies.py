from typing import Annotated

from fastapi import Depends

from app.todos.repository import TodoRepository
from app.todos.service import TodoService


def get_todo_service() -> TodoService:
    return TodoService(repository=TodoRepository())


type TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
