from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class MessageDTO:
    id: str
    chat_id: str
    sender_id: str
    text: str
    is_deleted: bool
    deleted_at: datetime | None
    edited_at: datetime | None
    reactions: dict
    read_by: list[str]
    created_at: datetime
    updated_at: datetime


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
