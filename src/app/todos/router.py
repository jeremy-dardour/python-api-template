from uuid import UUID

from fastapi import APIRouter

from app.core.problem_detail import NOT_FOUND_RESPONSE, VALIDATION_ERROR_RESPONSE
from app.todos.dependencies import TodoServiceDep
from app.todos.schemas import TodoRead

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


@router.get("")
async def get_todos(service: TodoServiceDep) -> list[TodoRead]:
    return await service.get_all()


@router.get("/{todo_id}", responses={404: NOT_FOUND_RESPONSE, 422: VALIDATION_ERROR_RESPONSE})
async def get_todo(todo_id: UUID, service: TodoServiceDep) -> TodoRead:
    return await service.get_by_id(todo_id)
