from httpx import AsyncClient


async def test_hello_world(client: AsyncClient) -> None:
    response = await client.get("/hello-world/")

    assert response.status_code == 200
    assert response.json() == "hello hello!"
