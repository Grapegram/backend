from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from msgspec import Struct

from src.core.chat.application.handlers.queries.get_chat_by_id import (
    GetChatById,
    GetChatByIdQuery,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class ChatMemberResponse(Struct):
    id: str
    user_id: str
    role: str


class ChatResponse(Struct):
    id: str
    title: str
    type: str
    avatar: str | None
    members: list[ChatMemberResponse]


@get(
    "/chats/{chat_id:str}",
    status_code=HTTP_200_OK,
    summary="Get chat by ID",
    description="Get details of a specific chat by its ID",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def get_chat_by_id(
    chat_id: str,
    current_user: str,
    handler: FromDishka[GetChatById] = None,
) -> ChatResponse:
    query = GetChatByIdQuery(chat_id=chat_id)
    result = await handler(query)

    if not result.chat:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Chat with id {chat_id} not found",
        )

    chat = result.chat

    return ChatResponse(
        id=chat.id,
        title=chat.title,
        type=chat.type,
        avatar=chat.avatar,
        members=[
            ChatMemberResponse(
                id=member.id,
                user_id=member.user_id,
                role=member.role,
            )
            for member in chat.members
        ],
    )
