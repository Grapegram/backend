from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from msgspec import Struct

from src.core.chat.application.handlers.queries.get_chats_list import (
    GetChatsList,
    GetChatsListQuery,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class ChatResponse(Struct):
    id: str
    title: str
    avatar: str | None
    is_archived: bool


class GetChatsListResponse(Struct):
    chats: list[ChatResponse]


@get(
    "/chats",
    status_code=HTTP_200_OK,
    summary="Get user's chats",
    description="Get a list of all chats where the current user is a member",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def get_chats_list(
    current_user: str,
    handler: FromDishka[GetChatsList] = None,
) -> GetChatsListResponse:
    try:
        query = GetChatsListQuery(user_id=current_user)
        result = await handler(query)

        chats = [
            ChatResponse(
                id=chat.id,
                title=chat.title,
                avatar=chat.avatar,
                is_archived=chat.is_archived,
            )
            for chat in result.chats
        ]

        return GetChatsListResponse(chats=chats)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to load chats: {str(e)}",
        )
