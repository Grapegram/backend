"""
MessageText Value Object

Represents a validated message text in the chat domain.
Encapsulates message text validation logic and provides
a type-safe way to work with message content.
"""

from dataclasses import dataclass
from typing import ClassVar

from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.value_objects import BoundedString
from seedwork.returns import catch_unwrap


@dataclass(frozen=True)
class InvalidMessageTextError(VOValidationException):
    """Exception raised when message text validation fails."""

    reason: str

    _msg_fmt: ClassVar[str] = "Invalid message text: {reason}"


class MessageText(BoundedString):
    """
    Message text value object with validation.

    Validates:
    - Minimum length (1 character - message cannot be empty)
    - Maximum length (4000 characters by default)
    - No leading/trailing whitespace only messages

    Examples:
        >>> result = MessageText("Hello, World!")
        >>> message_text = result.unwrap()
        >>> str(message_text)
        'Hello, World!'

        >>> result = MessageText("")
        >>> result.is_successful()
        False

        >>> result = MessageText("   ")
        >>> result.is_successful()
        False
    """

    MIN_LENGTH: int = 1
    MAX_LENGTH: int = 4000

    @classmethod
    @catch_unwrap
    def validate(cls, value: str) -> Result[str, VOValidationException]:
        """
        Validate message text.

        Args:
            value: The message text string to validate

        Returns:
            Success with the message text or Failure with InvalidMessageTextError
        """
        super().validate(value).unwrap()

        # Check if message is only whitespace
        if not value.strip():
            return Failure(
                InvalidMessageTextError(
                    reason="Message text cannot be empty or whitespace only"
                )
            )

        return Success(value)

    @property
    def trimmed(self) -> str:
        """Get the trimmed version of the message text."""
        return self._value.strip()

    @property
    def word_count(self) -> int:
        """Get the number of words in the message."""
        return len(self._value.split())

    def contains(self, substring: str) -> bool:
        """Check if message contains a substring (case-insensitive)."""
        return substring.lower() in self._value.lower()

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        """Return representation of the message text."""
        preview = self._value[:50] + "..." if len(self._value) > 50 else self._value
        return f"MessageText('{preview}')"

    def __eq__(self, other) -> bool:
        """Compare message texts."""
        if isinstance(other, MessageText):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        """Enable using MessageText as dict key or in sets."""
        return hash(self._value)
