"""
Chat Domain Layer

This module contains the domain model for the chat bounded context,
including aggregates, entities, value objects, events, and business rules.
"""

from .aggregates import Chat, Message
from .entities import Member, MemberRole
from .events import (
    ChatArchived,
    ChatCreated,
    ChatTitleChanged,
    ChatUnarchived,
    MemberAdded,
    MemberRemoved,
    MemberRoleChanged,
    MessageDeleted,
    MessageEdited,
    MessageReactionAdded,
    MessageReactionRemoved,
    MessageRead,
    MessageSent,
)
from .value_objects import ChatId, ChatTitle, MemberId, MessageId, MessageText

__all__ = [
    # Aggregates
    "Chat",
    "Message",
    # Entities
    "Member",
    "MemberRole",
    # Value Objects
    "ChatId",
    "MessageId",
    "MemberId",
    "MessageText",
    "ChatTitle",
    # Events - Chat
    "ChatCreated",
    "ChatTitleChanged",
    "MemberAdded",
    "MemberRemoved",
    "MemberRoleChanged",
    "ChatArchived",
    "ChatUnarchived",
    # Events - Message
    "MessageSent",
    "MessageEdited",
    "MessageDeleted",
    "MessageReactionAdded",
    "MessageReactionRemoved",
    "MessageRead",
]
