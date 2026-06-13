from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.todos.repository import TodoRepository
from app.todos.service import TodoService

# Repo root: src/app/todos/dependencies.py -> parents[3] is the project root.
# In a production app this path comes from settings (core/config.py); it is hardcoded
# here to keep the template free of a configuration layer for now.
_TODOS_CSV_PATH = Path(__file__).resolve().parents[3] / "data" / "todos.csv"


# Infrastructure: the data source, resolved at the route boundary. This is the
# override seam for integration tests (point it at a temporary CSV).
def get_todos_csv_path() -> Path:
    return _TODOS_CSV_PATH


TodosCsvPathDep = Annotated[Path, Depends(get_todos_csv_path)]


# One provider function per layer. The provider is FastAPI-aware; the domain class
# it builds is not (TodoRepository takes a plain Path, no Depends in its signature).
def get_todo_repository(csv_path: TodosCsvPathDep) -> TodoRepository:
    return TodoRepository(csv_path)


TodoRepositoryDep = Annotated[TodoRepository, Depends(get_todo_repository)]


def get_todo_service(repository: TodoRepositoryDep) -> TodoService:
    return TodoService(repository)


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]
