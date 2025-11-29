"""
ChatTitle Value Object

Represents a validated chat title in the chat domain.
Encapsulates chat title validation logic and provides
a type-safe way to work with chat titles.
"""

from dataclasses import dataclass
from typing import ClassVar

from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.value_objects import BoundedString
from seedwork.returns import catch_unwrap


@dataclass(frozen=True)
class InvalidChatTitleError(VOValidationException):
    """Exception raised when chat title validation fails."""

    reason: str

    _msg_fmt: ClassVar[str] = "Invalid chat title: {reason}"


class ChatTitle(BoundedString):
    """
    Chat title value object with validation.

    Validates:
    - Minimum length (1 character - title cannot be empty)
    - Maximum length (100 characters by default)
    - No leading/trailing whitespace only titles

    Examples:
        >>> result = ChatTitle("Project Discussion")
        >>> title = result.unwrap()
        >>> str(title)
        'Project Discussion'

        >>> result = ChatTitle("")
        >>> result.is_successful()
        False

        >>> result = ChatTitle("   ")
        >>> result.is_successful()
        False
    """

    MIN_LENGTH: int = 1
    MAX_LENGTH: int = 100

    @classmethod
    @catch_unwrap
    def validate(cls, value: str) -> Result[str, VOValidationException]:
        """
        Validate chat title.

        Args:
            value: The chat title string to validate

        Returns:
            Success with the chat title or Failure with InvalidChatTitleError
        """
        super().validate(value).unwrap()

        # Check if title is only whitespace
        if not value.strip():
            return Failure(
                InvalidChatTitleError(
                    reason="Chat title cannot be empty or whitespace only"
                )
            )

        return Success(value)

    @property
    def trimmed(self) -> str:
        """Get the trimmed version of the chat title."""
        return self._value.strip()

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        """Return representation of the chat title."""
        return f"ChatTitle('{self._value}')"

    def __eq__(self, other) -> bool:
        """Compare chat titles."""
        if isinstance(other, ChatTitle):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        """Enable using ChatTitle as dict key or in sets."""
        return hash(self._value)
