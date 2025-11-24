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

from src.core.chat.application.use_cases.add_reaction import AddReaction, FailedStatuses
from src.core.chat.presentation.api.guards import get_current_user_id


class AddReactionRequest(Struct):
    message_id: str
    reaction: str


@post(
    "/messages/reactions",
    status_code=HTTP_200_OK,
    summary="Add reaction to message",
    description="Add an emoji reaction to a message",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def add_reaction(
    data: Annotated[AddReactionRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[AddReaction],
    current_user: str,
) -> None:
    state = State(
        message_id=data.message_id,
        user_id=current_user,
        reaction=data.reaction,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                FailedStatuses.MESSAGE_NOT_FOUND: "Message not found",
                FailedStatuses.MESSAGE_DELETED: "Cannot react to a deleted message",
                FailedStatuses.INVALID_REACTION: "Invalid reaction",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Failed to add reaction"),
                extra={"error_code": error_status.value},
            )
