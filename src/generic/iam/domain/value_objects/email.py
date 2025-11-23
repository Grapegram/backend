import re
from dataclasses import dataclass
from typing import ClassVar

from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.value_objects import ValueObject


@dataclass(frozen=True)
class InvalidEmailError(VOValidationException):
    """Exception raised when email validation fails."""

    email: str
    reason: str

    _msg_fmt: ClassVar[str] = "Invalid email '{email}': {reason}"


class Email(ValueObject):
    """
    Email value object with comprehensive validation.

    Validates:
    - Format: Contains @ symbol with local and domain parts
    - Length: Local part <= 64 chars, domain <= 255 chars, total <= 320 chars
    - Characters: Valid characters in local and domain parts
    - Domain: At least one dot in domain part

    Examples:
        >>> result = Email("user@example.com")
        >>> result.unwrap()
        Email('user@example.com')

        >>> result = Email("invalid")
        >>> result.is_successful()
        False

        >>> email1 = Email("test@example.com").unwrap()
        >>> email2 = Email("test@example.com").unwrap()
        >>> email1 == email2
        True
    """

    # RFC 5321 limits
    MAX_LOCAL_LENGTH = 64
    MAX_DOMAIN_LENGTH = 255
    MAX_EMAIL_LENGTH = 320

    # Simple regex pattern for email validation
    # More permissive than strict RFC compliance for practical use
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"  # Local part
        r"@"
        r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?"  # Domain part
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?)*$"
    )

    _value: str

    def __init__(self, email: str) -> None:
        self._value = Email.normalize(email)

    @classmethod
    def validate(cls, email: str) -> Result[str, VOValidationException]:
        """
        Validate email address and return normalized version.

        Args:
            email: The email address string to validate

        Returns:
            Success with normalized email string or Failure with InvalidEmailError
        """
        if not email or not isinstance(email, str):
            return Failure(
                InvalidEmailError(email=str(email), reason="Email cannot be empty")
            )

        # Normalize: strip whitespace and convert to lowercase
        normalized = Email.normalize(email)

        # Validate length
        if len(normalized) > cls.MAX_EMAIL_LENGTH:
            return Failure(
                InvalidEmailError(
                    email=email,
                    reason=f"Email too long (max {cls.MAX_EMAIL_LENGTH} characters)",
                )
            )

        # Check for @ symbol
        if "@" not in normalized:
            return Failure(
                InvalidEmailError(email=email, reason="Email must contain @ symbol")
            )

        # Split into local and domain parts
        try:
            local_part, domain_part = normalized.rsplit("@", 1)
        except ValueError:
            return Failure(
                InvalidEmailError(
                    email=email, reason="Email must have exactly one @ symbol"
                )
            )

        # Validate local part
        if not local_part:
            return Failure(
                InvalidEmailError(email=email, reason="Local part cannot be empty")
            )

        if len(local_part) > cls.MAX_LOCAL_LENGTH:
            return Failure(
                InvalidEmailError(
                    email=email,
                    reason=f"Local part too long (max {cls.MAX_LOCAL_LENGTH} characters)",
                )
            )

        # Validate domain part
        if not domain_part:
            return Failure(
                InvalidEmailError(email=email, reason="Domain part cannot be empty")
            )

        if len(domain_part) > cls.MAX_DOMAIN_LENGTH:
            return Failure(
                InvalidEmailError(
                    email=email,
                    reason=f"Domain part too long (max {cls.MAX_DOMAIN_LENGTH} characters)",
                )
            )

        if "." not in domain_part:
            return Failure(
                InvalidEmailError(
                    email=email, reason="Domain must contain at least one dot"
                )
            )

        # Validate against regex pattern
        if not cls.EMAIL_PATTERN.match(normalized):
            return Failure(
                InvalidEmailError(email=email, reason="Invalid email format")
            )

        return Success(normalized)

    @property
    def local_part(self) -> str:
        """Get the local part of the email (before @)."""
        return self._value.split("@")[0]

    @property
    def domain(self) -> str:
        """Get the domain part of the email (after @)."""
        return self._value.split("@")[1]

    @property
    def normalized(self) -> str:
        """Get the normalized (lowercase) email address."""
        return str(self._value)

    @staticmethod
    def normalize(email: str) -> str:
        """Normalize email by stripping whitespace and converting to lowercase."""
        return email.strip().lower()

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email('{self._value}')"

    def __hash__(self) -> int:
        """Enable using Email as dict key or in sets."""
        return hash(self._value)

    def __eq__(self, other) -> bool:
        """Compare emails (case-insensitive)."""
        if isinstance(other, Email):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other.lower()
        return False
