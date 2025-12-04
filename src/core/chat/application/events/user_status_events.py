"""
User Status Application Events

Events related to user online status and typing indicators.
These are application-level events (not domain events) that trigger
infrastructure-level side effects like updating Redis.
"""

from dataclasses import dataclass

from seedwork.domain.events import DomainEvent


@dataclass(frozen=True)
class UserOnline(DomainEvent):
    """Event raised when user comes online or refreshes their presence"""

    user_id: str
    device_id: str


@dataclass(frozen=True)
class UserOffline(DomainEvent):
    """Event raised when user goes offline or disconnects"""

    user_id: str
    device_id: str


@dataclass(frozen=True)
class UserTypingStarted(DomainEvent):
    """Event raised when user starts typing in a chat"""

    user_id: str
    chat_id: str


@dataclass(frozen=True)
class UserTypingStopped(DomainEvent):
    """Event raised when user stops typing in a chat"""

    user_id: str
    chat_id: str
