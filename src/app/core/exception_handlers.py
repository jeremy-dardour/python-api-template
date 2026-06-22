from http import HTTPStatus
from typing import cast

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.errors import DomainError
from app.core.problem_detail import FieldError, ProblemDetail, ValidationProblemDetail

logger = structlog.stdlib.get_logger()

PROBLEM_JSON = "application/problem+json"


def _problem_response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type=PROBLEM_JSON,
    )


def _to_field_error(error: dict[str, object]) -> FieldError:
    location = cast("tuple[str | int, ...]", error.get("loc", ()))
    field = ".".join(str(part) for part in location)
    return FieldError(
        field=field,
        message=str(error.get("msg", "")),
        type=str(error.get("type", "")),
    )


def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    """Map domain exceptions to Problem Details using status/title from the error class."""
    return _problem_response(
        ProblemDetail(
            title=exc.title,
            status=exc.status,
            detail=exc.detail,
            instance=request.url.path,
        )
    )


def _handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Override Starlette's built-in handler so HTTPException also returns Problem Details."""
    title = HTTPStatus(exc.status_code).phrase
    response = _problem_response(
        ProblemDetail(
            title=title,
            status=exc.status_code,
            detail=str(exc.detail),
            instance=request.url.path,
        )
    )
    if exc.headers:
        response.headers.update(exc.headers)
    return response


def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Convert FastAPI request validation errors to Problem Details with per-field errors."""
    raw_errors = cast("list[dict[str, object]]", exc.errors())
    field_errors = [_to_field_error(error) for error in raw_errors]
    return _problem_response(
        ValidationProblemDetail(
            title="Validation Error",
            status=422,
            detail="Request body contains invalid fields.",
            instance=request.url.path,
            errors=field_errors,
        )
    )


def _handle_unhandled_error(request: Request, _exc: Exception) -> JSONResponse:
    """Catch-all that logs the traceback and returns a generic 500 with no internals leaked."""
    logger.exception("unhandled_error", method=request.method, path=request.url.path)
    return _problem_response(
        ProblemDetail(
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred.",
            instance=request.url.path,
        )
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers to return Problem Details responses."""
    # Starlette types handlers as (Request, Exception) but dispatches by exception class,
    # so narrowed signatures work at runtime. This is a known Starlette typing limitation.
    app.add_exception_handler(DomainError, _handle_domain_error)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(HTTPException, _handle_http_exception)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(Exception, _handle_unhandled_error)
