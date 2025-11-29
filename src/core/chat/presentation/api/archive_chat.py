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

from src.core.chat.application.use_cases.archive_chat import ArchiveChat
from src.core.chat.application.use_cases.archive_chat import (
    FailedStatuses as ArchiveFailedStatuses,
)
from src.core.chat.application.use_cases.unarchive_chat import (
    FailedStatuses as UnarchiveFailedStatuses,
)
from src.core.chat.application.use_cases.unarchive_chat import UnarchiveChat
from src.core.chat.presentation.api.guards import get_current_user_id


class ArchiveChatRequest(Struct):
    chat_id: str


class UnarchiveChatRequest(Struct):
    chat_id: str


@patch(
    "/chats/archive",
    status_code=HTTP_200_OK,
    summary="Archive chat",
    description="Archive a chat (admin only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def archive_chat(
    data: Annotated[ArchiveChatRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[ArchiveChat],
    current_user: str,
) -> None:
    state = State(
        chat_id=data.chat_id,
        archived_by=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                ArchiveFailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                ArchiveFailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                ArchiveFailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins or owners can archive the chat",
                ArchiveFailedStatuses.ALREADY_ARCHIVED: "Chat is already archived",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status
                in [
                    ArchiveFailedStatuses.INSUFFICIENT_PERMISSIONS,
                    ArchiveFailedStatuses.USER_NOT_MEMBER,
                ]
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to archive chat"),
                extra={"error_code": error_status.value},
            )


@patch(
    "/chats/unarchive",
    status_code=HTTP_200_OK,
    summary="Unarchive chat",
    description="Unarchive a chat (admin only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def unarchive_chat(
    data: Annotated[UnarchiveChatRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[UnarchiveChat],
    current_user: str,
) -> None:
    state = State(
        chat_id=data.chat_id,
        unarchived_by=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                UnarchiveFailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                UnarchiveFailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                UnarchiveFailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins or owners can unarchive the chat",
                UnarchiveFailedStatuses.NOT_ARCHIVED: "Chat is not archived",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status
                in [
                    UnarchiveFailedStatuses.INSUFFICIENT_PERMISSIONS,
                    UnarchiveFailedStatuses.USER_NOT_MEMBER,
                ]
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to unarchive chat"),
                extra={"error_code": error_status.value},
            )
