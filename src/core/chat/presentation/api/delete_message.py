from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import delete
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.delete_message import (
    DeleteMessage,
    FailedStatuses,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class DeleteMessageRequest(Struct):
    message_id: str


@delete(
    "/messages",
    status_code=HTTP_200_OK,
    summary="Delete message",
    description="Delete a message from a chat",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def delete_message(
    data: Annotated[DeleteMessageRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[DeleteMessage],
    current_user: str,
) -> None:
    state = State(
        message_id=data.message_id,
        deleter_id=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                FailedStatuses.MESSAGE_NOT_FOUND: "Message not found",
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "User is not a member of this chat",
                FailedStatuses.INSUFFICIENT_PERMISSIONS: "Insufficient permissions to delete this message",
                FailedStatuses.ALREADY_DELETED: "Message is already deleted",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status == FailedStatuses.INSUFFICIENT_PERMISSIONS
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to delete message"),
                extra={"error_code": error_status.value},
            )
