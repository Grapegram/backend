from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query
from src.core.chat.application.contracts.repositories import ChatReadRepository
from src.core.chat.application.contracts.repositories.chat_read_repository import (
    MessageDTO,
)


@dataclass(frozen=True)
class LoadMessagesFromChatQuery(Query):
    chat_id: str
    from_message_id: str | None = None
    limit: int = 50


@dataclass(frozen=True)
class LoadMessagesFromChatResult:
    messages: list[MessageDTO]
    limit: int
    has_more: bool


@dataclass
class LoadMessagesFromChat(Handler):
    handled = LoadMessagesFromChatQuery

    chat_read_repo: ChatReadRepository

    async def handle(
        self, query: LoadMessagesFromChatQuery
    ) -> LoadMessagesFromChatResult:
        messages = await self.chat_read_repo.get_messages_by_chat_id(
            chat_id=query.chat_id,
            from_message_id=query.from_message_id,
            limit=query.limit + 1,
        )

        has_more = len(messages) > query.limit
        if has_more:
            messages = messages[: query.limit]

        return LoadMessagesFromChatResult(
            messages=messages,
            limit=query.limit,
            has_more=has_more,
        )
