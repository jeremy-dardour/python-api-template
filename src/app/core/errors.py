class DomainError(Exception):
    status: int = 500
    title: str = "Internal Server Error"
    detail: str

    def __init__(self, detail: str) -> None:
        if type(self) is DomainError:
            raise TypeError("DomainError is abstract; raise a specific subclass instead.")
        self.detail = detail
        super().__init__(detail)


class NotFoundError(DomainError):
    status: int = 404
    title: str = "Not Found"


class ConflictError(DomainError):
    status: int = 409
    title: str = "Conflict"


class DomainValidationError(DomainError):
    status: int = 422
    title: str = "Validation Error"


class AuthorizationError(DomainError):
    status: int = 403
    title: str = "Forbidden"
