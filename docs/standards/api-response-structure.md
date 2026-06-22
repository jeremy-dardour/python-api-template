# Response Structure — fast-api-16.06.2026-responses

See [ADR 015](../adrs/015-response_structure.md) for the decision.

## Principle

Success responses return bare domain models. Error responses use RFC 9457 (Problem Details). Metadata goes in HTTP headers.

## Success responses

Endpoints return Pydantic models directly. No envelope.

```python
@router.get("/{todo_id}")
async def get_todo(todo_id: UUID, service: TodoServiceDep) -> TodoRead:
    return await service.get_by_id(todo_id)

@router.get("")
async def get_todos(service: TodoServiceDep) -> list[TodoRead]:
    return await service.get_all()
```

## Paginated list responses

Pagination is domain data, not metadata. Use a typed response model per resource.

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    next_cursor: str | None = None
```

## Domain exception hierarchy

Exceptions live in `app.core.errors`. They are purely domain concepts with no HTTP knowledge. Naming follows Python convention: `Error` suffix for all domain exceptions.

```
DomainError(Exception)          # base for all domain errors
├── NotFoundError               # resource does not exist
├── ConflictError               # duplicate or state conflict
├── DomainValidationError       # business rule violation
└── AuthorizationError          # insufficient permissions
```

Each exception carries a `detail` message string for entity-specific context.

## Error responses (RFC 9457)

All errors conform to Problem Details. Content-Type: `application/problem+json`. The `type` field defaults to `"about:blank"` per RFC 9457, meaning the type is identified solely by the status code.

```json
// 404 Not Found
{
  "type": "about:blank",
  "title": "Not Found",
  "status": 404,
  "detail": "Todo 550e8400-e29b-41d4-a716-446655440000 does not exist.",
  "instance": "/api/v1/todos/550e8400-e29b-41d4-a716-446655440000"
}

// 422 Validation Error (overrides FastAPI default)
{
  "type": "about:blank",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request body contains invalid fields.",
  "errors": [
    {
      "field": "name",
      "message": "Field required",
      "type": "missing"
    }
  ]
}

// 409 Conflict
{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "A todo with this name already exists."
}

// 500 Internal Server Error (no internals leaked)
{
  "type": "about:blank",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred."
}
```

## Exception handler wiring

```
Service raises DomainError
  └── app.core.exception_handlers maps to ProblemDetail response
        ├── NotFoundError         → 404
        ├── ConflictError         → 409
        ├── DomainValidationError → 422
        ├── AuthorizationError    → 403
        ├── RequestValidationError → 422 (ValidationProblemDetail with errors field)
        └── catch-all Exception   → 500 (generic body, logs traceback)
```

`register_exception_handlers(app)` in `app.core.exception_handlers` wires all handlers. Called once from `main.py`.

## Response models

- `ProblemDetail`: base Pydantic model with the five RFC 9457 fields (`type`, `title`, `status`, `detail`, `instance`).
- `ValidationProblemDetail(ProblemDetail)`: adds `errors: list[FieldError]` for structured per-field validation info from Pydantic.

Extensions are added as subclasses, not optional fields on the base.
