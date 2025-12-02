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

from src.core.chat.application.use_cases.delete_chat import DeleteChat
from src.core.chat.application.use_cases.delete_chat import (
    FailedStatuses as DeleteFailedStatuses,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class DeleteChatRequest(Struct):
    chat_id: str


@delete(
    "/chats",
    status_code=HTTP_200_OK,
    summary="Delete chat",
    description="Delete a chat (owner only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def delete_chat(
    data: Annotated[DeleteChatRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[DeleteChat],
    current_user: str,
) -> None:
    state = State(
        chat_id=data.chat_id,
        deleted_by=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                DeleteFailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                DeleteFailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                DeleteFailedStatuses.INSUFFICIENT_PERMISSIONS: "Only the owner can delete the chat",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status
                in [
                    DeleteFailedStatuses.INSUFFICIENT_PERMISSIONS,
                    DeleteFailedStatuses.USER_NOT_MEMBER,
                ]
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to delete chat"),
                extra={"error_code": error_status.value},
            )
