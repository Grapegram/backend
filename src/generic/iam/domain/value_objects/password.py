"""
Password Value Object

Represents a validated password in the IAM domain.
Encapsulates password validation logic, strength checking, and provides
a type-safe way to work with passwords.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.value_objects import BoundedString
from seedwork.returns import catch_unwrap


@dataclass(frozen=True)
class InvalidPasswordError(VOValidationException):
    """Exception raised when password validation fails."""

    reason: str

    _msg_fmt: ClassVar[str] = "Invalid password: {reason}"


@dataclass(frozen=True)
class WeakPasswordError(VOValidationException):
    """Exception raised when password is too weak."""

    reason: str
    missing_requirements: list[str]

    _msg_fmt: ClassVar[str] = "Weak password: {reason}"


class PasswordStrength(Enum):
    """Enumeration of password strength levels."""

    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class Password(BoundedString):
    """
    Plain text password value object with validation.

    This represents an unhashed password that should only exist
    temporarily during registration or password change flows.

    Validates:
    - Minimum length (8 characters by default)
    - Maximum length (128 characters to prevent DoS)
    - Optional strength requirements (uppercase, lowercase, digits, special chars)

    Examples:
        >>> result = Password("SecurePass123!")
        >>> password = result.unwrap()
        >>> password.strength
        PasswordStrength.STRONG

        >>> result = Password("weak")
        >>> result.is_successful()
        False

    Security Note:
        - Never log plain passwords
        - Never store plain passwords
        - Hash immediately after validation
        - Clear from memory after use
    """

    MIN_LENGTH: int = 8
    MAX_LENGTH: int = 128
    REQUIRE_UPPERCASE: bool = False
    REQUIRE_LOWERCASE: bool = False
    REQUIRE_DIGIT: bool = False
    REQUIRE_SPECIAL: bool = False

    # Character sets for strength checking
    UPPERCASE_PATTERN = re.compile(r"[A-Z]")
    LOWERCASE_PATTERN = re.compile(r"[a-z]")
    DIGIT_PATTERN = re.compile(r"\d")
    SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]")

    @classmethod
    @catch_unwrap
    def validate(cls, value: str) -> Result[str, VOValidationException]:
        super().validate(value).unwrap()

        # Check for whitespace (optional - some policies disallow it)
        if value.strip() != value:
            return Failure(
                InvalidPasswordError(
                    reason="Password cannot start or end with whitespace"
                )
            )

        # Strength requirements
        if any(
            [
                cls.REQUIRE_UPPERCASE,
                cls.REQUIRE_LOWERCASE,
                cls.REQUIRE_DIGIT,
                cls.REQUIRE_SPECIAL,
            ]
        ):
            missing = []

            if cls.REQUIRE_UPPERCASE and not cls.UPPERCASE_PATTERN.search(value):
                missing.append("uppercase letter")

            if cls.REQUIRE_LOWERCASE and not cls.LOWERCASE_PATTERN.search(value):
                missing.append("lowercase letter")

            if cls.REQUIRE_DIGIT and not cls.DIGIT_PATTERN.search(value):
                missing.append("digit")

            if cls.REQUIRE_SPECIAL and not cls.SPECIAL_CHAR_PATTERN.search(value):
                missing.append("special character")

            if missing:
                return Failure(
                    WeakPasswordError(
                        reason=f"Password must contain: {', '.join(missing)}",
                        missing_requirements=missing,
                    )
                )

        return Success(value)

    @property
    def strength(self) -> PasswordStrength:
        """
        Calculate password strength.

        Returns:
            PasswordStrength level based on criteria met
        """
        score = 0

        # Length scoring
        if len(self) >= 8:
            score += 1
        if len(self) >= 12:
            score += 1
        if len(self) >= 16:
            score += 1

        # Character diversity scoring
        if self.UPPERCASE_PATTERN.search(self._value):
            score += 1
        if self.LOWERCASE_PATTERN.search(self._value):
            score += 1
        if self.DIGIT_PATTERN.search(self._value):
            score += 1
        if self.SPECIAL_CHAR_PATTERN.search(self._value):
            score += 1

        # Map score to strength
        if score <= 2:
            return PasswordStrength.WEAK
        elif score <= 4:
            return PasswordStrength.MEDIUM
        elif score <= 6:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.VERY_STRONG

    def has_uppercase(self) -> bool:
        """Check if password contains uppercase letters."""
        return bool(self.UPPERCASE_PATTERN.search(self._value))

    def has_lowercase(self) -> bool:
        """Check if password contains lowercase letters."""
        return bool(self.LOWERCASE_PATTERN.search(self._value))

    def has_digit(self) -> bool:
        """Check if password contains digits."""
        return bool(self.DIGIT_PATTERN.search(self._value))

    def has_special_char(self) -> bool:
        """Check if password contains special characters."""
        return bool(self.SPECIAL_CHAR_PATTERN.search(self._value))

    def meets_requirements(self) -> bool:
        """Check if password meets all configured requirements."""
        if self.REQUIRE_UPPERCASE and not self.has_uppercase():
            return False
        if self.REQUIRE_LOWERCASE and not self.has_lowercase():
            return False
        if self.REQUIRE_DIGIT and not self.has_digit():
            return False
        if self.REQUIRE_SPECIAL and not self.has_special_char():
            return False
        return True

    def __str__(self) -> str:
        """Return masked password for safety."""
        return "********"

    def __repr__(self) -> str:
        """Return safe representation."""
        return f"Password(length={self.length}, strength={self.strength.value})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Password):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value)
