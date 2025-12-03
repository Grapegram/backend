from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class MessageDTO:
    id: str
    chat_id: str
    sender_id: str
    text: str | None
    images: list[str]
    sent_at: datetime
    edited_at: datetime | None
    reactions: dict[str, list[str]]
    read_by: list[str]


@dataclass(frozen=True)
class ChatMemberDTO:
    id: str
    user_id: str
    role: str
    joined_at: datetime


@dataclass(frozen=True)
class ChatDTO:
    id: str
    title: str
    type: str
    avatar: str | None
    members: list[ChatMemberDTO]


class ChatReadRepository(Protocol):
    """
    Read-only repository for chat queries.

    This repository is optimized for read operations and bypasses
    the domain layer for performance (CQRS read model).
    """

    async def get_messages_by_chat_id(
        self, chat_id: str, limit: int, offset: int
    ) -> list[MessageDTO]: ...

    async def count_messages_by_chat_id(self, chat_id: str) -> int: ...

    async def get_chats_by_member_user_id(self, user_id: str) -> list[ChatDTO]: ...

    async def get_chat_by_id(self, chat_id: str) -> ChatDTO | None: ...
