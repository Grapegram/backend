from dataclasses import dataclass
from typing import Any, ClassVar

from seedwork.exceptions import FormattedError


@dataclass
class RepositoryException(FormattedError):
    """Base exception for repository operations."""

    _msg_fmt: ClassVar[str] = "Repository operation failed"


@dataclass
class EntityNotFoundException(RepositoryException):
    """Exception raised when an entity is not found in the repository."""

    entity_id: Any
    entity_type: str

    _msg_fmt: ClassVar[str] = "Entity {entity_type} with id {entity_id} not found"


@dataclass
class RepositoryConnectionException(RepositoryException):
    """Exception raised when repository cannot connect to storage."""

    reason: str

    _msg_fmt: ClassVar[str] = "Repository connection failed: {reason}"


@dataclass
class RepositoryOperationException(RepositoryException):
    """Exception raised when a repository operation fails."""

    operation: str
    reason: str

    _msg_fmt: ClassVar[str] = "Repository operation '{operation}' failed: {reason}"
