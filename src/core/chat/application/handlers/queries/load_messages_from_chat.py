from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query
from src.core.chat.application.contracts.repositories import ChatReadRepository
from src.core.chat.application.contracts.repositories.chat_read_repository import (
    MessageDTO,
)


@dataclass(frozen=True)
class LoadMessagesFromChatQuery(Query):
    chat_id: str
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class LoadMessagesFromChatResult:
    messages: list[MessageDTO]
    total_count: int
    limit: int
    offset: int
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
            limit=query.limit,
            offset=query.offset,
        )

        total_count = await self.chat_read_repo.count_messages_by_chat_id(query.chat_id)

        has_more = (query.offset + query.limit) < total_count

        return LoadMessagesFromChatResult(
            messages=messages,
            total_count=total_count,
            limit=query.limit,
            offset=query.offset,
            has_more=has_more,
        )
