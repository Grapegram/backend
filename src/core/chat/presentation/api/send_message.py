from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.send_message import FailedStatuses, SendMessage
from src.core.chat.presentation.api.guards import get_current_user_id


class SendMessageRequest(Struct):
    chat_id: str
    text: str


class SendMessageResponse(Struct):
    message_id: str
    chat_id: str
    sender_id: str
    text: str


@post(
    "/messages",
    status_code=HTTP_201_CREATED,
    summary="Send message",
    description="Send a new message in a chat",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def send_message(
    data: Annotated[SendMessageRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[SendMessage],
    current_user: str,
) -> SendMessageResponse:
    state = State(
        chat_id=data.chat_id,
        sender_id=current_user,
        text=data.text,
    )
    await story(state)

    match state.result:
        case Success(message):
            return SendMessageResponse(
                message_id=str(message.id),
                chat_id=str(message.chat_id),
                sender_id=message.sender_id,
                text=str(message.text),
            )
        case Failure(error_status):
            error_messages = {
                FailedStatuses.INVALID_INPUT: "Invalid message data",
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "User is not a member of this chat",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Failed to send message"),
                extra={"error_code": error_status.value},
            )
