import time
import uuid
from http import HTTPStatus
from typing import override

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = structlog.stdlib.get_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status, duration, and request ID for every request."""

    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Clear at entry instead of unbinding at exit. An unhandled exception unwinds past this
        # middleware out to Starlette's ServerErrorMiddleware (which runs outside all user
        # middleware and renders the 500); we want request_id still bound when its handler logs.
        # Clearing here keeps each request isolated without removing the binding on the error path.
        structlog.contextvars.clear_contextvars()
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        _ = structlog.contextvars.bind_contextvars(request_id=request_id)

        start = time.monotonic()
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # finally, not except: every request, including crashes, gets exactly one access line.
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            logger.info(
                "request",
                method=request.method,
                path=request.url.path,
                status=status,
                duration_ms=duration_ms,
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach browser security headers to every response."""

    def __init__(self, app: ASGIApp, *, environment: str) -> None:
        super().__init__(app)
        self.environment: str = environment

    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        if self.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
