from app.models.todos import Todo
from app.repositories.todos import TodoRepository
from app.schemas.todos import TodoRead


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self._repository: TodoRepository = repository

    async def get_all(self) -> list[TodoRead]:
        todos: list[Todo] = await self._repository.get_all()
        return [self._to_schema(todo) for todo in todos]

    @staticmethod
    def _to_schema(todo: Todo) -> TodoRead:
        return TodoRead(
            id=todo.id,
            name=todo.name,
            status=todo.status,
        )
