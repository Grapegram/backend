from typing import Annotated

from dishka.integrations.litestar import FromDishka
from litestar import post
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.generic.iam.application.use_cases.registration import (
    FailedStatuses,
    Registeration,
)


class RegisterRequest(Struct):
    email: str
    username: str
    password: str


@post(
    "/register",
    status_code=HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user with email, username and password",
)
async def register(
    self,
    data: Annotated[RegisterRequest, Body(media_type=RequestEncodingType.JSON)],
    *,
    story: FromDishka[Registeration],
) -> None:
    state = State(
        email=data.email,
        username=data.username,
        password=data.password,
    )
    await story(state)

    match state.result:
        case Success():
            return None
        case Failure(error_status):
            error_messages = {
                FailedStatuses.EMAIL_ALREADY_EXISTS: "Email is already registered",
                FailedStatuses.USERNAME_ALREADY_EXISTS: "Username is already taken",
                FailedStatuses.INVALID_CREDENTIALS: "Invalid registration data",
            }

            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_messages.get(error_status, "Registration failed"),
                extra={"error_code": error_status.value},
            )
