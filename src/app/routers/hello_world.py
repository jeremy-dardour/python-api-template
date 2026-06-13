from fastapi import APIRouter

router = APIRouter(
    prefix="/hello-world",
    tags=["hello-world"],
)


@router.get("")
async def hello_world() -> str:
    return "hello hello!"
