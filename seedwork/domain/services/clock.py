from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstract clock interface for testable datetime operations."""

    @abstractmethod
    def now(self) -> datetime:
        """Return the current datetime."""
        pass


class SystemClock(Clock):
    """System clock implementation using real datetime."""

    def now(self) -> datetime:
        """Return the current UTC datetime."""
        return datetime.utcnow()


class FixedClock(Clock):
    """Fixed clock implementation for testing."""

    def __init__(self, fixed_time: datetime):
        """
        Initialize with a fixed time.

        Args:
            fixed_time: The fixed datetime to return
        """
        self._fixed_time = fixed_time

    def now(self) -> datetime:
        """Return the fixed datetime."""
        return self._fixed_time

    def set_time(self, new_time: datetime) -> None:
        """
        Update the fixed time.

        Args:
            new_time: The new fixed datetime
        """
        self._fixed_time = new_time


# Global clock instance
_clock: Clock | None = None


def get_clock() -> Clock:
    """
    Get the current clock instance.

    Returns:
        The current clock instance (defaults to SystemClock if not set)
    """
    global _clock
    if _clock is None:
        _clock = SystemClock()
    return _clock


def set_clock(clock: Clock) -> None:
    """
    Set the global clock instance.

    Args:
        clock: The clock instance to use
    """
    global _clock
    _clock = clock


def reset_clock() -> None:
    """Reset the clock to use SystemClock."""
    global _clock
    _clock = SystemClock()


def utcnow() -> datetime:
    """
    Convenience function to get current UTC datetime.

    Returns:
        Current datetime from the configured clock
    """
    return get_clock().now()
