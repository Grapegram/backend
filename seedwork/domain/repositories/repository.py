from typing import Protocol, TypeVar

from returns.maybe import Maybe
from returns.result import Result

from seedwork.domain.entities import AggregateRoot, EntityId
from seedwork.domain.repositories.exceptions import EntityNotFoundException

TEntity = TypeVar("TEntity", bound=AggregateRoot, covariant=True)


class Repository(Protocol[EntityId, TEntity]):
    """
    Base repository protocol for aggregate persistence.

    Repositories are responsible for persisting and retrieving aggregates.
    They act as a collection-like interface to the underlying storage mechanism.
    """

    async def save(self, entity: TEntity) -> None: ...

    async def get(self, entity_id: EntityId) -> Maybe[TEntity]: ...

    async def delete(
        self, entity_id: EntityId
    ) -> Result[None, EntityNotFoundException]: ...

    async def exists(self, entity_id: EntityId) -> bool: ...
