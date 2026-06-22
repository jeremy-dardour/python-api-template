from pydantic import BaseModel


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None


class FieldError(BaseModel):
    field: str
    message: str
    type: str


class ValidationProblemDetail(ProblemDetail):
    errors: list[FieldError]


NOT_FOUND_RESPONSE_EXAMPLE: dict[str, object] = {
    "model": ProblemDetail,
    "content": {
        "application/problem+json": {
            "example": {
                "type": "about:blank",
                "title": "Not Found",
                "status": 404,
                "detail": "Resource does not exist.",
                "instance": "/api/v1/resource/123",
            }
        }
    },
}

VALIDATION_ERROR_RESPONSE_EXAMPLE: dict[str, object] = {
    "model": ValidationProblemDetail,
    "content": {
        "application/problem+json": {
            "example": {
                "type": "about:blank",
                "title": "Validation Error",
                "status": 422,
                "detail": "Request body contains invalid fields.",
                "instance": "/api/v1/resource",
                "errors": [
                    {
                        "field": "body.name",
                        "message": "Field required",
                        "type": "missing",
                    }
                ],
            }
        }
    },
}
