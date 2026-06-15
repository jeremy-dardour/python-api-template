from httpx import AsyncClient


class TestHelloWorld:
    async def test_hello_world(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/hello-world")

        assert response.status_code == 200
        assert response.json() == "hello hello!"
