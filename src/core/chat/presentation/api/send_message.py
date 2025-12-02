from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.send_message import FailedStatuses, SendMessage
from src.core.chat.presentation.api.guards import get_current_user_id

# Maximum file size per image: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024

# Maximum number of images per message
MAX_IMAGES = 10

# Allowed content types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
}


class SendMessageRequest(Struct):
    chat_id: str
    text: str | None = None
    images: list[UploadFile] | None = None


class SendMessageResponse(Struct):
    message_id: str
    chat_id: str
    sender_id: str
    text: str
    images: list[str]


@post(
    "/messages",
    status_code=HTTP_201_CREATED,
    summary="Send message",
    description="Send a new message in a chat with optional image attachments (max 10 images)",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def send_message(
    data: Annotated[
        SendMessageRequest, Body(media_type=RequestEncodingType.MULTI_PART)
    ],
    story: FromDishka[SendMessage] = None,
    current_user: str = None,
) -> SendMessageResponse:
    images = data.images
    # Validate that at least text or images are provided
    if not data.text and not images:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Message must have either text or at least one image",
        )

    # Validate number of images
    if images and len(images) > MAX_IMAGES:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_IMAGES} images allowed per message",
        )

    # Process image files if provided
    image_files = []
    print(images)
    if images:
        for img in images:
            # Validate content type
            if img.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file type: {img.content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
                )

            # Read image data
            image_data = await img.read()

            # Validate file size
            if len(image_data) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Image size exceeds maximum allowed size of {MAX_IMAGE_SIZE / (1024 * 1024)}MB",
                )

            # Validate file is not empty
            if len(image_data) == 0:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Uploaded image file is empty",
                )

            print(img.content_type)
            image_files.append((image_data, img.content_type))

    state = State(
        chat_id=data.chat_id,
        sender_id=current_user,
        text=data.text or None,
        image_files=image_files if image_files else None,
    )
    await story(state)

    match state.result:
        case Success(message):
            return SendMessageResponse(
                message_id=str(message.id),
                chat_id=str(message.chat_id),
                sender_id=message.sender_id,
                text=str(message.text) if message.text else "",
                images=message.images,
            )
        case Failure(error_status):
            error_messages = {
                FailedStatuses.INVALID_INPUT: "Invalid message data",
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.USER_NOT_MEMBER: "User is not a member of this chat",
                FailedStatuses.UPLOAD_FAILED: "Failed to upload images to storage",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Failed to send message"),
                extra={"error_code": error_status.value},
            )
