from typing import Annotated

from fastapi import Depends

from app.repositories.todos import TodoRepository
from app.services.todos import TodoService


def get_todo_service() -> TodoService:
    return TodoService(repository=TodoRepository())


type TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
