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

from src.core.chat.application.use_cases.create_chat import CreateChat, FailedStatuses
from src.core.chat.presentation.api.guards import get_current_user_id


class CreateChatRequest(Struct):
    title: str


class CreateChatResponse(Struct):
    chat_id: str
    title: str


@post(
    "/chats",
    status_code=HTTP_201_CREATED,
    summary="Create new chat",
    description="Create a new chat with the specified title",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def create_chat(
    data: Annotated[CreateChatRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[CreateChat],
    current_user: str,
) -> CreateChatResponse:
    state = State(
        title=data.title,
        created_by=current_user,
    )
    await story(state)

    match state.result:
        case Success(chat):
            return CreateChatResponse(
                chat_id=str(chat.id),
                title=str(chat.title),
            )
        case Failure(error_status):
            error_messages = {
                FailedStatuses.INVALID_INPUT: "Invalid chat data",
                FailedStatuses.USER_NOT_FOUND: "User not found",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Failed to create chat"),
                extra={"error_code": error_status.value},
            )
