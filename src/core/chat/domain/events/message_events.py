"""
Message Domain Events

Events related to the Message aggregate lifecycle and operations.
"""

from dataclasses import dataclass
from datetime import datetime

from seedwork.domain.events import DomainEvent

from ..value_objects import ChatId, MessageId


@dataclass(frozen=True)
class MessageSent(DomainEvent):
    """Event raised when a new message is sent"""

    message_id: MessageId
    chat_id: ChatId
    sender_id: str
    text: str
    images: list[str]
    sent_at: datetime


@dataclass(frozen=True)
class MessageEdited(DomainEvent):
    """Event raised when a message is edited"""

    message_id: MessageId
    chat_id: ChatId
    old_text: str
    new_text: str
    edited_by: str
    edited_at: datetime


@dataclass(frozen=True)
class MessageDeleted(DomainEvent):
    """Event raised when a message is deleted"""

    message_id: MessageId
    chat_id: ChatId
    deleted_by: str
    deleted_at: datetime


@dataclass(frozen=True)
class MessageReactionAdded(DomainEvent):
    """Event raised when a reaction is added to a message"""

    message_id: MessageId
    chat_id: ChatId
    user_id: str
    reaction: str
    added_at: datetime


@dataclass(frozen=True)
class MessageReactionRemoved(DomainEvent):
    """Event raised when a reaction is removed from a message"""

    message_id: MessageId
    chat_id: ChatId
    user_id: str
    reaction: str
    removed_at: datetime


@dataclass(frozen=True)
class MessageRead(DomainEvent):
    """Event raised when a message is read by a user"""

    message_id: MessageId
    chat_id: ChatId
    user_id: str
    read_at: datetime
