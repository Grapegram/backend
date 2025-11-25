from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import post
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_410_GONE
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.generic.iam.application.use_cases.verification_email import (
    FailedStatuses,
    VerifyEmail,
)


class VerificationEmailRequest(Struct):
    token: str


@post(
    "/verify-email",
    status_code=HTTP_200_OK,
    summary="Verify email address",
    description="Verify user's email address using verification token",
)
@inject
async def verify_email(
    data: Annotated[
        VerificationEmailRequest, Body(media_type=RequestEncodingType.JSON)
    ],
    story: FromDishka[VerifyEmail],
) -> None:
    state = State(
        verification_token=data.token,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            if error_status == FailedStatuses.TOKEN_EXPIRED:
                raise HTTPException(
                    status_code=HTTP_410_GONE,
                    detail="Verification token has expired",
                    extra={"error_code": error_status.value},
                )

            error_messages = {
                FailedStatuses.MISSING_TOKEN: "Verification token is required",
                FailedStatuses.INVALID_TOKEN: "Invalid verification token",
                FailedStatuses.INVALID_TOKEN_TYPE: "Invalid token type",
                FailedStatuses.USER_NOT_FOUND: "User not found",
                FailedStatuses.ALREADY_VERIFIED: "Email is already verified",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Email verification failed"),
                extra={"error_code": error_status.value},
            )
