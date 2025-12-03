from datetime import datetime
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
    text: str | None
    images: list[str]
    sent_at: datetime
    edited_at: datetime | None
    reactions: dict[str, list[str]]
    read_by: list[str]


class LoadMessagesResponse(Struct):
    messages: list[MessageResponse]
    limit: int
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
    from_message_id: Annotated[
        str | None,
        Parameter(
            default=None,
            description="Message ID to load messages before (for cursor-based pagination)",
        ),
    ] = None,
    handler: FromDishka[LoadMessagesFromChat] = None,
) -> LoadMessagesResponse:
    try:
        query = LoadMessagesFromChatQuery(
            chat_id=chat_id,
            from_message_id=from_message_id,
            limit=limit,
        )
        result = await handler(query)

        messages = [
            MessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                sender_id=msg.sender_id,
                text=msg.text,
                images=msg.images,
                sent_at=msg.sent_at,
                edited_at=msg.edited_at,
                reactions=msg.reactions,
                read_by=msg.read_by,
            )
            for msg in result.messages
        ]

        return LoadMessagesResponse(
            messages=messages,
            limit=result.limit,
            has_more=result.has_more,
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to load messages: {str(e)}",
        )
