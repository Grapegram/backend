from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query

from ...contracts.repositories import ChatReadRepository
from ...contracts.repositories.chat_read_repository import ChatDTO


@dataclass(frozen=True)
class GetChatByIdQuery(Query):
    chat_id: str


@dataclass(frozen=True)
class GetChatByIdResult:
    chat: ChatDTO | None


@dataclass
class GetChatById(Handler):
    handled = GetChatByIdQuery

    chat_read_repo: ChatReadRepository

    async def handle(self, query: GetChatByIdQuery) -> GetChatByIdResult:
        chat = await self.chat_read_repo.get_chat_by_id(query.chat_id)

        return GetChatByIdResult(chat=chat)
