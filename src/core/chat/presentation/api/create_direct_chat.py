from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.create_direct_chat import (
    CreateDirectChat,
)
from src.core.chat.application.use_cases.create_direct_chat import (
    FailedStatuses as DirectChatFailedStatuses,
)
from src.core.chat.presentation.api.guards import get_current_user_id


class CreateDirectChatRequest(Struct):
    other_user_id: str


class CreateDirectChatResponse(Struct):
    chat_id: str


@post(
    "/chats/direct",
    status_code=HTTP_200_OK,
    summary="Create or get direct chat",
    description="Create a new direct chat with another user, or return existing one",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def create_direct_chat(
    data: Annotated[CreateDirectChatRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[CreateDirectChat],
    current_user: str,
) -> CreateDirectChatResponse:
    state = State(
        user1_id=current_user,
        user2_id=data.other_user_id,
    )
    await story(state)

    match state.result:
        case Success(chat):
            return CreateDirectChatResponse(
                chat_id=str(chat.id),
            )
        case Failure(error_status):
            error_messages = {
                DirectChatFailedStatuses.INVALID_INPUT: "Invalid input data",
                DirectChatFailedStatuses.CANNOT_CREATE_CHAT_WITH_SELF: "Cannot create a direct chat with yourself",
                DirectChatFailedStatuses.CHAT_ALREADY_EXISTS: "Direct chat already exists",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Failed to create direct chat"),
                extra={"error_code": error_status.value},
            )
