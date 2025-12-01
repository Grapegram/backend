from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query

from ...contracts.repositories import ChatReadRepository
from ...contracts.repositories.chat_read_repository import ChatDTO


@dataclass(frozen=True)
class GetChatsListQuery(Query):
    user_id: str


@dataclass(frozen=True)
class GetChatsListResult:
    chats: list[ChatDTO]


@dataclass
class GetChatsList(Handler):
    handled = GetChatsListQuery

    chat_read_repo: ChatReadRepository

    async def handle(self, query: GetChatsListQuery) -> GetChatsListResult:
        chats = await self.chat_read_repo.get_chats_by_member_user_id(query.user_id)

        return GetChatsListResult(chats=chats)
