import csv
from pathlib import Path
from uuid import UUID

from app.todos.models import Todo, TodoStatus


class TodoRepository:
    def __init__(self, csv_path: Path) -> None:
        self._csv_path: Path = csv_path

    async def get_all(self) -> list[Todo]:
        return self._read_all()

    async def get_by_id(self, todo_id: UUID) -> Todo | None:
        for todo in self._read_all():
            if todo.id == todo_id:
                return todo
        return None

    def _read_all(self) -> list[Todo]:
        with self._csv_path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [
                Todo(
                    id=UUID(row["id"]),
                    name=row["name"],
                    status=TodoStatus(row["status"]),
                )
                for row in reader
            ]
