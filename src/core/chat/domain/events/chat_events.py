"""
Chat Domain Events

Events related to the Chat aggregate lifecycle and operations.
"""

from dataclasses import dataclass
from datetime import datetime

from seedwork.domain.events import DomainEvent

from ..value_objects import ChatId


@dataclass(frozen=True)
class ChatCreated(DomainEvent):
    """Event raised when a new chat is created"""

    chat_id: ChatId
    title: str
    created_by: str
    created_at: datetime


@dataclass(frozen=True)
class ChatTitleChanged(DomainEvent):
    """Event raised when chat title is changed"""

    chat_id: ChatId
    old_title: str
    new_title: str
    changed_by: str
    changed_at: datetime


@dataclass(frozen=True)
class MemberAdded(DomainEvent):
    """Event raised when a member is added to the chat"""

    chat_id: ChatId
    member_id: str
    user_id: str
    role: str
    added_by: str
    added_at: datetime


@dataclass(frozen=True)
class MemberRemoved(DomainEvent):
    """Event raised when a member is removed from the chat"""

    chat_id: ChatId
    member_id: str
    user_id: str
    removed_by: str
    removed_at: datetime


@dataclass(frozen=True)
class MemberRoleChanged(DomainEvent):
    """Event raised when a member's role is changed"""

    chat_id: ChatId
    member_id: str
    old_role: str
    new_role: str
    changed_by: str
    changed_at: datetime


@dataclass(frozen=True)
class ChatArchived(DomainEvent):
    """Event raised when a chat is archived"""

    chat_id: ChatId
    archived_by: str
    archived_at: datetime


@dataclass(frozen=True)
class ChatUnarchived(DomainEvent):
    """Event raised when a chat is unarchived"""

    chat_id: ChatId
    unarchived_by: str
    unarchived_at: datetime
