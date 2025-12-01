from dataclasses import dataclass

from seedwork.application.handlers import Handler, Query

from ...contracts.repositories import UserDTO, UserReadRepository


@dataclass(frozen=True)
class GetCurrentUserQuery(Query):
    user_id: str


@dataclass(frozen=True)
class GetCurrentUserResult:
    user: UserDTO


@dataclass
class GetCurrentUser(Handler):
    handled = GetCurrentUserQuery

    user_read_repo: UserReadRepository

    async def handle(self, query: GetCurrentUserQuery) -> GetCurrentUserResult:
        user = await self.user_read_repo.get_user_by_id(query.user_id)

        if user is None:
            raise ValueError(f"User with id {query.user_id} not found")

        return GetCurrentUserResult(user=user)
