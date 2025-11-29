from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from msgspec import Struct

from src.core.chat.application.handlers.queries.load_messages_from_chat import (
    LoadMessagesFromChat,
    LoadMessagesFromChatQuery,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class MessageResponse(Struct):
    id: str
    chat_id: str
    sender_id: str
    text: str
    is_deleted: bool
    reactions: dict
    read_by: list[str]


class LoadMessagesResponse(Struct):
    messages: list[MessageResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool


@get(
    "/chats/{chat_id:str}/messages",
    status_code=HTTP_200_OK,
    summary="Load chat messages",
    description="Load paginated messages from a chat",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def load_messages(
    chat_id: Annotated[str, Parameter(description="Chat ID")],
    limit: Annotated[
        int,
        Parameter(default=50, ge=1, le=100, description="Number of messages to load"),
    ] = 50,
    offset: Annotated[
        int, Parameter(default=0, ge=0, description="Offset for pagination")
    ] = 0,
    handler: FromDishka[LoadMessagesFromChat] = None,
) -> LoadMessagesResponse:
    try:
        query = LoadMessagesFromChatQuery(
            chat_id=chat_id,
            limit=limit,
            offset=offset,
        )
        result = await handler(query)

        messages = [
            MessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                text=msg.text,
                is_deleted=msg.is_deleted,
                reactions=msg.reactions,
                read_by=msg.read_by,
            )
            for msg in result.messages
        ]

        return LoadMessagesResponse(
            messages=messages,
            total_count=result.total_count,
            limit=result.limit,
            offset=result.offset,
            has_more=result.has_more,
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to load messages: {str(e)}",
        )
