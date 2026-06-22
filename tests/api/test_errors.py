# pyright: reportAny=false, reportUnusedFunction=false
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.errors import (
    AuthorizationError,
    ConflictError,
    DomainValidationError,
    NotFoundError,
)
from app.core.exception_handlers import register_exception_handlers

PROBLEM_JSON = "application/problem+json"


@pytest.fixture
async def error_client() -> AsyncGenerator[AsyncClient]:
    error_app = FastAPI()
    register_exception_handlers(error_app)

    @error_app.get("/not-found")
    async def _not_found() -> None:
        raise NotFoundError("Thing 123 does not exist.")

    @error_app.get("/conflict")
    async def _conflict() -> None:
        raise ConflictError("A thing with this name already exists.")

    @error_app.get("/domain-validation")
    async def _domain_validation() -> None:
        raise DomainValidationError("Name must not be empty.")

    @error_app.get("/authorization")
    async def _authorization() -> None:
        raise AuthorizationError("You do not have access to this resource.")

    @error_app.get("/validate/{item_id}")
    async def _validate(item_id: UUID) -> dict[str, str]:
        return {"id": str(item_id)}

    @error_app.get("/boom")
    async def _boom() -> None:
        raise RuntimeError("kaboom")

    async with AsyncClient(
        transport=ASGITransport(app=error_app, raise_app_exceptions=False),
        base_url="http://test",
    ) as ac:
        yield ac


class TestNotFoundError:
    async def test_returns_404_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/not-found")

        assert response.status_code == 404
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Not Found"
        assert body["status"] == 404
        assert body["detail"] == "Thing 123 does not exist."
        assert body["instance"] == "/not-found"


class TestConflictError:
    async def test_returns_409_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/conflict")

        assert response.status_code == 409
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Conflict"
        assert body["status"] == 409
        assert body["detail"] == "A thing with this name already exists."


class TestDomainValidationError:
    async def test_returns_422_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/domain-validation")

        assert response.status_code == 422
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Validation Error"
        assert body["status"] == 422
        assert body["detail"] == "Name must not be empty."


class TestAuthorizationError:
    async def test_returns_403_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/authorization")

        assert response.status_code == 403
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Forbidden"
        assert body["status"] == 403
        assert body["detail"] == "You do not have access to this resource."


class TestRequestValidationError:
    async def test_invalid_uuid_returns_422_with_field_errors(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/validate/not-a-uuid")

        assert response.status_code == 422
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Validation Error"
        assert body["status"] == 422
        assert "detail" in body
        assert isinstance(body["errors"], list)
        assert len(body["errors"]) > 0
        error = body["errors"][0]
        assert "field" in error
        assert "message" in error
        assert "type" in error


class TestUnhandledError:
    async def test_returns_500_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/boom")

        assert response.status_code == 500
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Internal Server Error"
        assert body["status"] == 500
        assert body["detail"] == "An unexpected error occurred."

    async def test_does_not_leak_internals(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/boom")

        body = response.json()
        assert "kaboom" not in body["detail"]
        assert "traceback" not in str(body).lower()
