from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from msgspec import Struct

from src.generic.iam.application.handlers.queries.get_current_user import (
    GetCurrentUser,
    GetCurrentUserQuery,
)
from src.generic.iam.presentation.api.guards import get_current_user_id


class CurrentUserResponse(Struct):
    id: str
    email: str
    username: str
    avatar: str | None
    is_active: bool
    is_verified: bool


@get(
    "",
    status_code=HTTP_200_OK,
    summary="Get current user",
    description="Get the authenticated user's profile",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def get_current_user(
    current_user: str,
    handler: FromDishka[GetCurrentUser],
) -> CurrentUserResponse:
    try:
        query = GetCurrentUserQuery(user_id=current_user)
        result = await handler(query)

        return CurrentUserResponse(
            id=result.user.id,
            email=result.user.email,
            username=result.user.username,
            avatar=result.user.avatar,
            is_active=result.user.is_active,
            is_verified=result.user.is_verified,
        )
    except ValueError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Failed to load user: {str(e)}",
        )
