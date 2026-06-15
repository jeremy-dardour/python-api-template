from fastapi import APIRouter

from app.hello_world.router import router as hello_world_router
from app.todos.router import router as todos_router

api_router = APIRouter()
api_router.include_router(todos_router)
api_router.include_router(hello_world_router)
