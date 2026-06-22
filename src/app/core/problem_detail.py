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
