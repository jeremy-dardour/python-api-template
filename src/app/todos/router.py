from uuid import UUID

from fastapi import APIRouter

from app.todos.dependencies import TodoServiceDep
from app.todos.schemas import TodoRead

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.get("")
async def get_todos(service: TodoServiceDep) -> list[TodoRead]:
    return await service.get_all()


@router.get("/{todo_id}")
async def get_todo(todo_id: UUID, service: TodoServiceDep) -> TodoRead:
    return await service.get_by_id(todo_id)
