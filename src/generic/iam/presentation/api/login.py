from typing import Annotated

from dishka.integrations.litestar import FromDishka
from litestar import post
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.generic.iam.application.use_cases.login import FailedStatuses, Login


class LoginRequest(Struct):
    credential: str
    password: str


class LoginResponse(Struct):
    access_token: str


@post(
    "/login",
    status_code=HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email/username and password",
)
async def login(
    self,
    data: Annotated[LoginRequest, Body(media_type=RequestEncodingType.JSON)],
    *,
    story: FromDishka[Login],
) -> LoginResponse:
    state = State(
        credential=data.credential,
        password=data.password,
    )
    await story(state)

    match state.result:
        case Success(auth_token):
            return LoginResponse(access_token=auth_token.access_token)
        case Failure(error_status):
            error_messages = {
                FailedStatuses.USER_NOT_FOUND: "Invalid credentials",
                FailedStatuses.INVALID_CREDENTIALS: "Invalid credentials",
                FailedStatuses.ACCOUNT_DEACTIVATED: "Account has been deactivated",
                FailedStatuses.MISSING_CREDENTIAL: "Credential is required",
                FailedStatuses.MISSING_PASSWORD: "Password is required",
            }

            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=error_messages.get(error_status, "Authentication failed"),
                extra={"error_code": error_status.value},
            )
