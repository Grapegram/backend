from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from msgspec import Struct

from src.generic.iam.application.handlers.queries.get_users_list import (
    GetUsersList,
    GetUsersListQuery,
)
from src.generic.iam.presentation.api.guards import get_current_user_id


class UserResponse(Struct):
    id: str
    email: str
    username: str
    avatar: str | None
    is_active: bool
    is_verified: bool


class GetUsersListResponse(Struct):
    users: list[UserResponse]


@get(
    "/users",
    status_code=HTTP_200_OK,
    summary="Get users list",
    description="Get a list of all users with optional filtering",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def get_users_list(
    search: Annotated[
        str | None,
        Parameter(
            default=None,
            description="Search by username or email",
        ),
    ] = None,
    is_active: Annotated[
        bool | None,
        Parameter(
            default=None,
            description="Filter by active status",
        ),
    ] = None,
    is_verified: Annotated[
        bool | None,
        Parameter(
            default=None,
            description="Filter by verification status",
        ),
    ] = None,
    handler: FromDishka[GetUsersList] = None,
) -> GetUsersListResponse:
    try:
        query = GetUsersListQuery(
            search=search,
            is_active=is_active,
            is_verified=is_verified,
        )
        result = await handler(query)

        users = [
            UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                avatar=user.avatar,
                is_active=user.is_active,
                is_verified=user.is_verified,
            )
            for user in result.users
        ]

        return GetUsersListResponse(users=users)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to load users: {str(e)}",
        )
