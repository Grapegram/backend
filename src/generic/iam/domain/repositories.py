from typing import Protocol

from returns.maybe import Maybe

from seedwork.domain.repositories import Repository

from .aggregates import User
from .value_objects.user_id import UserId


class UserRepository(Repository[UserId, User], Protocol):
    """
    Repository for User aggregate.

    Extends base Repository with user-specific query methods.
    """

    async def get_by_email(self, email: str) -> Maybe[User]: ...

    async def get_by_username(self, username: str) -> Maybe[User]: ...
