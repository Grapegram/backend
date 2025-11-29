from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import patch
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.change_chat_title import (
    ChangeChatTitle,
    FailedStatuses,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class ChangeChatTitleRequest(Struct):
    chat_id: str
    new_title: str


@patch(
    "/chats/title",
    status_code=HTTP_200_OK,
    summary="Change chat title",
    description="Change the title of an existing chat (admin only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def change_chat_title(
    data: Annotated[ChangeChatTitleRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[ChangeChatTitle],
    current_user: str,
) -> None:
    state = State(
        chat_id=data.chat_id,
        new_title=data.new_title,
        changed_by=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                FailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins or owners can change the chat title",
                FailedStatuses.INVALID_TITLE: "Invalid chat title",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status
                in [
                    FailedStatuses.INSUFFICIENT_PERMISSIONS,
                    FailedStatuses.USER_NOT_MEMBER,
                ]
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to change chat title"),
                extra={"error_code": error_status.value},
            )
