"""
Reaction Value Object

Represents a validated reaction (emoji) in the chat domain.
Encapsulates reaction validation logic and provides
a type-safe way to work with message reactions.
"""

import re
from dataclasses import dataclass
from typing import ClassVar

from returns.result import Failure, Result, Success

from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.value_objects import ValueObject


@dataclass(frozen=True)
class InvalidReactionError(VOValidationException):
    """Exception raised when reaction validation fails."""

    reaction: str
    reason: str

    _msg_fmt: ClassVar[str] = "Invalid reaction '{reaction}': {reason}"


class Reaction(ValueObject):
    """
    Reaction value object with validation.

    Validates:
    - Must be a valid emoji or emoji sequence
    - Cannot be empty
    - Maximum length (to prevent abuse with long emoji sequences)

    Examples:
        >>> result = Reaction("👍")
        >>> reaction = result.unwrap()
        >>> str(reaction)
        '👍'

        >>> result = Reaction("❤️")
        >>> reaction.is_successful()
        True

        >>> result = Reaction("")
        >>> result.is_successful()
        False
    """

    MAX_LENGTH: int = 20  # Maximum characters for emoji sequence

    # Common emoji patterns (Unicode ranges for emojis)
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002702-\U000027b0"  # dingbats
        "\U000024c2-\U0001f251"  # enclosed characters
        "\U0001f900-\U0001f9ff"  # supplemental symbols and pictographs
        "\U0001fa00-\U0001fa6f"  # chess symbols
        "\U0001fa70-\U0001faff"  # symbols and pictographs extended-a
        "\U00002600-\U000026ff"  # miscellaneous symbols
        "\U00002700-\U000027bf"  # dingbats
        "\ufe0f"  # variation selector
        "\u200d"  # zero width joiner
        "]+",
        flags=re.UNICODE,
    )

    # Predefined common reactions (optional whitelist)
    COMMON_REACTIONS = {
        "👍",
        "👎",
        "❤️",
        "😂",
        "😮",
        "😢",
        "😡",
        "🎉",
        "🔥",
        "👏",
        "✅",
        "❌",
        "⭐",
        "💯",
        "🙏",
        "💪",
        "👀",
        "🤔",
        "😍",
        "🚀",
    }

    _value: str

    def __init__(self, reaction: str) -> None:
        self._value = reaction

    @classmethod
    def validate(cls, value: str) -> Result[str, VOValidationException]:
        """
        Validate reaction emoji.

        Args:
            value: The reaction string to validate

        Returns:
            Success with the reaction or Failure with InvalidReactionError
        """
        if not value or not isinstance(value, str):
            return Failure(
                InvalidReactionError(
                    reaction=str(value), reason="Reaction cannot be empty"
                )
            )

        # Strip whitespace
        value = value.strip()

        if not value:
            return Failure(
                InvalidReactionError(
                    reaction=value, reason="Reaction cannot be empty or whitespace"
                )
            )

        # Check length
        if len(value) > cls.MAX_LENGTH:
            return Failure(
                InvalidReactionError(
                    reaction=value,
                    reason=f"Reaction too long (max {cls.MAX_LENGTH} characters)",
                )
            )

        # Check if it contains emoji characters
        if not cls.EMOJI_PATTERN.search(value):
            return Failure(
                InvalidReactionError(
                    reaction=value,
                    reason="Reaction must contain valid emoji characters",
                )
            )

        return Success(value)

    @property
    def emoji(self) -> str:
        """Get the emoji string."""
        return self._value

    def is_common(self) -> bool:
        """Check if this is a commonly used reaction."""
        return self._value in self.COMMON_REACTIONS

    def __repr__(self) -> str:
        """Return representation of the reaction."""
        return f"Reaction('{self._value}')"

    def __str__(self) -> str:
        """Return the emoji string."""
        return self._value

    def __eq__(self, other) -> bool:
        """Compare reactions."""
        if isinstance(other, Reaction):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return False

    def __hash__(self) -> int:
        """Enable using Reaction as dict key or in sets."""
        return hash(self._value)
