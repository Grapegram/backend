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

from src.generic.iam.application.use_cases.change_user_avatar import (
    ChangeUserAvatar,
    FailedStatuses,
)
from src.generic.iam.presentation.api.guards import get_current_user_id

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


class ChangeUserAvatarResponse(Struct):
    avatar: str | None


@put(
    "/avatar",
    status_code=HTTP_200_OK,
    summary="Upload user avatar",
    description="Upload a new avatar image for the authenticated user",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def upload_user_avatar(
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    story: FromDishka[ChangeUserAvatar],
    current_user: str,
) -> ChangeUserAvatarResponse:
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
        user_id=current_user,
        image_data=image_data,
        content_type=data.content_type,
    )
    await story(state)

    match state.result:
        case Success(avatar):
            return ChangeUserAvatarResponse(avatar=avatar)
        case Failure(error_status):
            error_messages = {
                FailedStatuses.USER_NOT_FOUND: "User not found",
                FailedStatuses.ACCOUNT_DEACTIVATED: "Account has been deactivated",
                FailedStatuses.UPLOAD_FAILED: "Failed to upload avatar to storage",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status == FailedStatuses.ACCOUNT_DEACTIVATED
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to change user avatar"),
                extra={"error_code": error_status.value},
            )


@delete(
    "/avatar",
    status_code=HTTP_200_OK,
    summary="Delete user avatar",
    description="Remove the avatar image from the authenticated user",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def delete_user_avatar(
    story: FromDishka[ChangeUserAvatar],
    current_user: str,
) -> ChangeUserAvatarResponse:
    state = State(
        user_id=current_user,
        image_data=None,
        content_type=None,
    )
    await story(state)

    match state.result:
        case Success(avatar):
            return ChangeUserAvatarResponse(avatar=avatar)
        case Failure(error_status):
            error_messages = {
                FailedStatuses.USER_NOT_FOUND: "User not found",
                FailedStatuses.ACCOUNT_DEACTIVATED: "Account has been deactivated",
                FailedStatuses.UPLOAD_FAILED: "Failed to remove avatar",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status == FailedStatuses.ACCOUNT_DEACTIVATED
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to delete user avatar"),
                extra={"error_code": error_status.value},
            )
