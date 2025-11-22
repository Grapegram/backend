from returns.maybe import Maybe, Nothing

from src.generic.iam.domain import User, UserId, UserRepository


class InMemoryUserRepository(UserRepository):
    """
    In-memory implementation of UserRepository for testing and development.

    Stores users in memory and provides async query methods.
    All entities are deep-copied on save/retrieve to prevent external mutations.
    """

    def __init__(self):
        self._storage: dict[UserId, User] = {}

    async def save(self, entity: User) -> None:
        self._storage[entity.id] = entity

    async def get(self, entity_id: UserId) -> Maybe[User]:
        entity = self._storage.get(entity_id)
        if entity is None:
            return Nothing
        return entity

    async def delete(self, entity_id: UserId) -> None:
        if entity_id in self._storage:
            del self._storage[entity_id]

    async def exists(self, entity_id: UserId) -> bool:
        return entity_id in self._storage

    async def get_by_email(self, email: str) -> Maybe[User]:
        for user in self._storage.values():
            if str(user.email) == email:
                return user
        return Nothing

    async def get_by_username(self, username: str) -> Maybe[User]:
        for user in self._storage.values():
            if user.username == username:
                return user
        return Nothing

    def clear(self) -> None:
        """Clear all users from storage. Useful for test cleanup."""
        self._storage.clear()

    def count(self) -> int:
        """Get the number of users in storage."""
        return len(self._storage)

    async def all(self) -> list[User]:
        """Get all users from storage."""
        return [user for user in self._storage.values()]
