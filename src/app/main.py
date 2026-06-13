from fastapi import FastAPI

from app.routers.hello_world import router as hello_world_router
from app.routers.todos import router as todos_router

app = FastAPI()

app.include_router(hello_world_router)
app.include_router(todos_router)
