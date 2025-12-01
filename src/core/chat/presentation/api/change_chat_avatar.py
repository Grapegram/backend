from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import delete, put
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.change_chat_avatar import (
    ChangeChatAvatar,
    FailedStatuses,
)
from src.core.chat.presentation.api.guards import get_current_user_id

# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed content types
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
}


class ChangeChatAvatarResponse(Struct):
    avatar: str | None


@put(
    "/chats/{chat_id:str}/avatar",
    status_code=HTTP_200_OK,
    summary="Upload chat avatar",
    description="Upload a new avatar image for a chat (admin only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def upload_chat_avatar(
    chat_id: str,
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    story: FromDishka[ChangeChatAvatar],
    current_user: str,
) -> ChangeChatAvatarResponse:
    # Validate content type
    if data.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    # Read file data
    image_data = await data.read()

    # Validate file size
    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB",
        )

    # Validate file is not empty
    if len(image_data) == 0:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    state = State(
        chat_id=chat_id,
        changed_by=current_user,
        image_data=image_data,
        content_type=data.content_type,
    )
    await story(state)

    match state.result:
        case Success(avatar):
            return ChangeChatAvatarResponse(avatar=avatar)
        case Failure(error_status):
            error_messages = {
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                FailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins or owners can change the chat avatar",
                FailedStatuses.INVALID_AVATAR_URL: "Invalid avatar URL",
                FailedStatuses.UPLOAD_FAILED: "Failed to upload avatar to storage",
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
                detail=error_messages.get(error_status, "Failed to change chat avatar"),
                extra={"error_code": error_status.value},
            )


@delete(
    "/chats/{chat_id:str}/avatar",
    status_code=HTTP_200_OK,
    summary="Delete chat avatar",
    description="Remove the avatar image from a chat (admin only)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def delete_chat_avatar(
    chat_id: str,
    story: FromDishka[ChangeChatAvatar],
    current_user: str,
) -> ChangeChatAvatarResponse:
    state = State(
        chat_id=chat_id,
        changed_by=current_user,
        image_data=None,
        content_type=None,
    )
    await story(state)

    match state.result:
        case Success(avatar):
            return ChangeChatAvatarResponse(avatar=avatar)
        case Failure(error_status):
            error_messages = {
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "You are not a member of this chat",
                FailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins or owners can change the chat avatar",
                FailedStatuses.INVALID_AVATAR_URL: "Invalid avatar URL",
                FailedStatuses.UPLOAD_FAILED: "Failed to remove avatar",
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
                detail=error_messages.get(error_status, "Failed to delete chat avatar"),
                extra={"error_code": error_status.value},
            )
