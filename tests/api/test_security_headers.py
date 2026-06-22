from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.middleware import SecurityHeadersMiddleware

ALWAYS_PRESENT_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Content-Security-Policy": "default-src 'none'",
}


async def test_security_headers_present(client: AsyncClient) -> None:
    response = await client.get("/health")

    for header, value in ALWAYS_PRESENT_HEADERS.items():
        assert response.headers[header] == value


async def test_hsts_absent_outside_production(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert "Strict-Transport-Security" not in response.headers


# HSTS is set at app construction time, so we need a separate app built with environment="production".
@pytest.fixture
async def production_client() -> AsyncGenerator[AsyncClient]:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, environment="production")

    @app.get("/test")
    def _() -> str:
        return "ok"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def test_hsts_present_in_production(production_client: AsyncClient) -> None:
    response = await production_client.get("/test")

    assert response.headers["Strict-Transport-Security"] == "max-age=63072000; includeSubDomains"
