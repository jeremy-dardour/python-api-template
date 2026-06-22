# pyright: reportAny=false, reportUnusedFunction=false
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.errors import (
    AuthorizationError,
    ConflictError,
    DomainError,
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

    class CreateBody(BaseModel):
        name: str

    @error_app.post("/validate-body")
    async def _validate_body(body: CreateBody) -> dict[str, str]:
        return {"name": body.name}

    @error_app.get("/boom")
    async def _boom() -> None:
        raise RuntimeError("kaboom")

    @error_app.get("/http-exception")
    async def _http_exception() -> None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    @error_app.get("/http-exception-with-headers")
    async def _http_exception_with_headers() -> None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    class SpecificNotFoundError(NotFoundError):
        pass

    @error_app.get("/subclass-error")
    async def _subclass_error() -> None:
        raise SpecificNotFoundError("Specific thing not found.")

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
        assert error["field"] == "path.item_id"
        assert "message" in error
        assert "type" in error

    async def test_body_validation_includes_source_prefix(self, error_client: AsyncClient) -> None:
        response = await error_client.post(
            "/validate-body",
            json={},
        )

        assert response.status_code == 422
        body = response.json()
        error = body["errors"][0]
        assert error["field"] == "body.name"


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


class TestHTTPException:
    async def test_returns_problem_detail(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/http-exception")

        assert response.status_code == 401
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["type"] == "about:blank"
        assert body["title"] == "Unauthorized"
        assert body["status"] == 401
        assert body["detail"] == "Not authenticated"

    async def test_preserves_headers(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/http-exception-with-headers")

        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


class TestDomainErrorSubclass:
    async def test_subclass_inherits_parent_status(self, error_client: AsyncClient) -> None:
        response = await error_client.get("/subclass-error")

        assert response.status_code == 404
        assert response.headers["content-type"] == PROBLEM_JSON
        body = response.json()
        assert body["title"] == "Not Found"
        assert body["detail"] == "Specific thing not found."


class TestDomainErrorIsAbstract:
    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError):
            _ = DomainError("should fail")
