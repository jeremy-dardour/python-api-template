import io
import logging
import uuid
from collections.abc import AsyncGenerator, Iterator

import pytest
import structlog
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestLoggingMiddleware

# capture_logs() strips the processor chain, so contextvar-bound keys (request_id) are dropped.
# Re-adding merge_contextvars surfaces them for assertions.
CAPTURE_CONTEXTVARS = [structlog.contextvars.merge_contextvars]


@pytest.fixture
def captured_root_output() -> Iterator[io.StringIO]:
    # Redirect the root handler to a buffer while reusing the app's real formatter, so the test
    # observes the genuine configured render pipeline (static service fields included) rather than
    # a reconstructed one. capture_logs() cannot be used here: it replaces the processor chain,
    # which is exactly where the static fields are injected.
    root_logger = logging.getLogger()
    real_handlers = root_logger.handlers[:]
    buffer = io.StringIO()
    capture_handler = logging.StreamHandler(buffer)
    if real_handlers:
        capture_handler.setFormatter(real_handlers[0].formatter)
    root_logger.handlers = [capture_handler]
    try:
        yield buffer
    finally:
        root_logger.handlers = real_handlers


@pytest.fixture
async def error_client() -> AsyncGenerator[AsyncClient]:
    # The real app exposes no endpoint that raises an unhandled exception, so the error path
    # needs a standalone app with a /boom route. raise_app_exceptions=False lets us observe the
    # rendered 500 instead of having the test client re-raise.
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)

    @app.get("/boom")
    def _() -> str:
        raise RuntimeError("boom")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_generates_request_id_when_absent(client: AsyncClient) -> None:
    response = await client.get("/health")

    # A valid UUID is generated and echoed back when the caller sends none.
    generated = response.headers["X-Request-ID"]
    assert uuid.UUID(generated).version == 4


async def test_echoes_incoming_request_id(client: AsyncClient) -> None:
    incoming = "client-supplied-id"

    response = await client.get("/health", headers={"X-Request-ID": incoming})

    assert response.headers["X-Request-ID"] == incoming


async def test_logs_request_summary(client: AsyncClient) -> None:
    with structlog.testing.capture_logs() as logs:
        _ = await client.get("/health")

    entries = [entry for entry in logs if entry["event"] == "request"]
    assert len(entries) == 1
    entry = entries[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status"] == 200
    assert isinstance(entry["duration_ms"], float)


async def test_unhandled_error_log_carries_request_id(error_client: AsyncClient) -> None:
    with structlog.testing.capture_logs(processors=CAPTURE_CONTEXTVARS) as logs:
        response = await error_client.get("/boom", headers={"X-Request-ID": "err-id"})

    assert response.status_code == 500
    error_logs = [entry for entry in logs if entry["event"] == "unhandled_error"]
    assert len(error_logs) == 1
    assert error_logs[0]["request_id"] == "err-id"


async def test_access_line_emitted_on_crash(error_client: AsyncClient) -> None:
    with structlog.testing.capture_logs(processors=CAPTURE_CONTEXTVARS) as logs:
        response = await error_client.get("/boom")

    assert response.status_code == 500
    access_logs = [entry for entry in logs if entry["event"] == "request"]
    assert len(access_logs) == 1
    assert access_logs[0]["status"] == 500
    assert access_logs[0]["path"] == "/boom"


async def test_logs_carry_service_metadata(
    client: AsyncClient,
    captured_root_output: io.StringIO,
) -> None:
    _ = await client.get("/health")

    output = captured_root_output.getvalue()
    settings = get_settings()
    assert "service" in output
    assert settings.app_name in output
    assert settings.app_version in output
    # environment is a deployment fact tagged by the log shipper, never self-reported by the app.
    assert "environment" not in output
