from typing import Protocol

from returns.maybe import Maybe

from seedwork.domain.repositories import Repository

from .aggregates import Chat, Message
from .value_objects import ChatId, MessageId


class ChatRepository(Repository[ChatId, Chat], Protocol):
    """
    Repository for Chat aggregate.

    Extends base Repository with chat-specific query methods.
    """

    async def get_by_user_id(self, user_id: str) -> list[Chat]: ...

    async def get_by_member_user_id(self, user_id: str) -> list[Chat]: ...

    async def get_direct_chat_between(
        self, user1_id: str, user2_id: str
    ) -> Maybe[Chat]: ...


class MessageRepository(Repository[MessageId, Message], Protocol):
    """
    Repository for Message aggregate.

    Extends base Repository with message-specific query methods.
    """

    async def get_by_chat_id(
        self, chat_id: str, limit: int = 50, offset: int = 0
    ) -> list[Message]: ...

    async def get_by_sender_id(self, sender_id: str) -> list[Message]: ...

    async def count_by_chat_id(self, chat_id: str) -> int: ...
