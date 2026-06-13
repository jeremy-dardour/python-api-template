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
