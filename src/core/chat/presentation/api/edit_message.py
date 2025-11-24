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

from src.core.chat.application.use_cases.edit_message import EditMessage, FailedStatuses
from src.core.chat.presentation.api.guards import get_current_user_id


class EditMessageRequest(Struct):
    message_id: str
    new_text: str


@patch(
    "/messages",
    status_code=HTTP_200_OK,
    summary="Edit message",
    description="Edit the text of an existing message",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def edit_message(
    data: Annotated[EditMessageRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[EditMessage],
    current_user: str,
) -> None:
    state = State(
        message_id=data.message_id,
        new_text=data.new_text,
        editor_id=current_user,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                FailedStatuses.MESSAGE_NOT_FOUND: "Message not found",
                FailedStatuses.ONLY_AUTHOR_CAN_EDIT: "Only the author can edit this message",
                FailedStatuses.MESSAGE_DELETED: "Cannot edit a deleted message",
                FailedStatuses.TEXT_UNCHANGED: "New text must be different from current text",
                FailedStatuses.INVALID_TEXT: "Invalid message text",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status == FailedStatuses.ONLY_AUTHOR_CAN_EDIT
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to edit message"),
                extra={"error_code": error_status.value},
            )
