from returns.maybe import Maybe, Nothing
from returns.result import Failure, Result

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.repositories.exceptions import EntityNotFoundException
from seedwork.domain.repositories.repository import Repository
from seedwork.domain.value_objects import GenericUUID


class InMemoryRepository[TEntityId: GenericUUID, TEntity: AggregateRoot](
    Repository[TEntityId, TEntity]
):
    """
    Generic in-memory repository implementation for testing.

    This repository stores entities in a dictionary and provides
    basic CRUD operations. It's useful for unit tests where you
    don't want to set up a real database.

    Example:
        >>> from generic.iam.domain import User, UserId
        >>> user_repo = InMemoryRepository[UserId, User]()
        >>> user = User.create(email="test@example.com", username="test")
        >>> user_repo.save(user)
        >>> retrieved = user_repo.get(user.id)
        >>> assert retrieved.id == user.id
    """

    def __init__(self):
        self._storage: dict[TEntityId, TEntity] = {}

    async def save(self, entity: TEntity) -> None:
        """
        Save an entity to in-memory storage.

        Args:
            entity: The entity to save
        """

        # Store a deep copy to prevent external mutations
        self._storage[entity.id] = entity

    async def get(self, entity_id: TEntityId) -> Maybe[TEntity]:
        """
        Retrieve an entity by ID.

        Args:
            entity_id: The unique identifier

        Returns:
            The entity if found, None otherwise
        """
        entity = self._storage.get(entity_id)
        if entity is None:
            return Nothing

        # Return a copy to prevent external mutations
        return entity

    async def delete(self, entity_id: TEntityId) -> Result[None, EntityNotFoundException]:
        """
        Delete an entity from storage.

        Args:
            entity_id: The unique identifier

        Raises:
            EntityNotFoundException: If the entity doesn't exist
        """
        if entity_id not in self._storage:
            return Failure(
                EntityNotFoundException(entity_id=entity_id, entity_type=type(self).__name__)
            )
        del self._storage[entity_id]

    async def exists(self, entity_id: TEntityId) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: The unique identifier

        Returns:
            True if the entity exists, False otherwise
        """
        return entity_id in self._storage

    async def clear(self) -> None:
        """
        Clear all entities from storage.

        This is useful for cleaning up between tests.
        """
        self._storage.clear()

    async def count(self) -> int:
        """
        Get the number of entities in storage.

        Returns:
            The count of stored entities
        """
        return len(self._storage)

    async def all(self) -> list[TEntity]:
        """
        Get all entities from storage.

        Returns:
            A list of all entities (as copies)
        """

        return [entity for entity in self._storage.values()]
