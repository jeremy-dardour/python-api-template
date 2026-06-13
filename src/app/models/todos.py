from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class TodoStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass(frozen=True)
class Todo:
    id: UUID
    name: str
    status: TodoStatus
