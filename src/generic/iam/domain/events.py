from dataclasses import dataclass
from datetime import datetime

from seedwork.domain.events import DomainEvent

from .value_objects import UserId


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    """Event raised when a new user is created"""

    user_id: UserId
    email: str
    username: str
    created_at: datetime


@dataclass(frozen=True)
class UserUpdated(DomainEvent):
    """Event raised when user information is updated"""

    user_id: UserId
    updated_at: datetime


@dataclass(frozen=True)
class UserDeactivated(DomainEvent):
    """Event raised when a user is deactivated"""

    user_id: UserId
    deactivated_at: datetime


@dataclass(frozen=True)
class UserActivated(DomainEvent):
    """Event raised when a user is activated"""

    user_id: UserId
    activated_at: datetime
