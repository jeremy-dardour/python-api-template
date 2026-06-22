import logging
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.errors import (
    AuthorizationError,
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)
from app.core.problem_detail import FieldError, ProblemDetail, ValidationProblemDetail

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"

_DOMAIN_ERROR_STATUS: dict[type[DomainError], tuple[int, str]] = {
    NotFoundError: (404, "Not Found"),
    ConflictError: (409, "Conflict"),
    DomainValidationError: (422, "Validation Error"),
    AuthorizationError: (403, "Forbidden"),
}


def _problem_response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(exclude_none=True),
        media_type=PROBLEM_JSON,
    )


async def _handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    status, title = _DOMAIN_ERROR_STATUS.get(type(exc), (500, "Internal Server Error"))
    return _problem_response(
        ProblemDetail(
            title=title,
            status=status,
            detail=exc.detail,
            instance=request.url.path,
        )
    )


async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
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


async def _handle_unhandled_error(request: Request, _exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _problem_response(
        ProblemDetail(
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred.",
            instance=request.url.path,
        )
    )


def _to_field_error(error: dict[str, object]) -> FieldError:
    location = cast("tuple[str | int, ...]", error.get("loc", ()))
    field = ".".join(str(part) for part in location if part != "body")
    return FieldError(
        field=field,
        message=str(error.get("msg", "")),
        type=str(error.get("type", "")),
    )


def register_exception_handlers(app: FastAPI) -> None:
    # Starlette types handlers as (Request, Exception) but dispatches by exception class,
    # so narrowed signatures work at runtime. This is a known Starlette typing limitation.
    app.add_exception_handler(DomainError, _handle_domain_error)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(Exception, _handle_unhandled_error)
