from fastapi import FastAPI

from app.hello_world.router import router as hello_world_router
from app.todos.router import router as todos_router

app = FastAPI()

app.include_router(hello_world_router)
app.include_router(todos_router)
