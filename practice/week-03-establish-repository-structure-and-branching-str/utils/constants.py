"""
System-wide constants and enumerations.
"""

from enum import Enum


class TaskStatus(str, Enum):
    """Lifecycle statuses for tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

    @classmethod
    def choices(cls):
        return [(status.value, status.name.replace('_', ' ').title()) for status in cls]


class TaskPriority(str, Enum):
    """Priority levels for task scheduling and triage."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def choices(cls):
        return [(priority.value, priority.name.title()) for priority in cls]


class HttpStatusCodes:
    """HTTP status code references."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
MAX_TITLE_LENGTH = 200
