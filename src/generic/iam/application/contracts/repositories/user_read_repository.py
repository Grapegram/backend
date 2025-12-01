from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class UserDTO:
    id: str
    email: str
    username: str
    avatar: str | None
    is_active: bool
    is_verified: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserListFilters:
    search: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


class UserReadRepository(Protocol):
    """
    Read-only repository for user queries.

    This repository is optimized for read operations and bypasses
    the domain layer for performance (CQRS read model).
    """

    async def get_users_list(self, filters: UserListFilters) -> list[UserDTO]: ...

    async def get_user_by_id(self, user_id: str) -> UserDTO | None: ...
