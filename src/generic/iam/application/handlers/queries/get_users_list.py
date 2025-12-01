from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query

from ...contracts.repositories import UserDTO, UserListFilters, UserReadRepository


@dataclass(frozen=True)
class GetUsersListQuery(Query):
    search: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


@dataclass(frozen=True)
class GetUsersListResult:
    users: list[UserDTO]


@dataclass
class GetUsersList(Handler):
    handled = GetUsersListQuery

    user_read_repo: UserReadRepository

    async def handle(self, query: GetUsersListQuery) -> GetUsersListResult:
        filters = UserListFilters(
            search=query.search,
            is_active=query.is_active,
            is_verified=query.is_verified,
        )

        users = await self.user_read_repo.get_users_list(filters=filters)

        return GetUsersListResult(users=users)
