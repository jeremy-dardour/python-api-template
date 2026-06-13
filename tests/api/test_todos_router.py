from httpx import AsyncClient
from pydantic import TypeAdapter

from app.schemas.todos import TodoRead


class TestGetTodosList:
    async def test_get_todos_list(self, client: AsyncClient) -> None:
        response = await client.get("/todos")

        assert response.status_code == 200
        todos = TypeAdapter(list[TodoRead]).validate_python(response.json())

        assert isinstance(response.json(), list)

        assert len(todos) == 3
        assert todos[0].name == "Buy groceries"
        assert todos[0].status == "pending"
        assert todos[0].id is not None
