from dataclasses import dataclass, field
from typing import TypeVar

from returns.result import Failure, Result, Success

from seedwork.domain.events import DomainEvent
from seedwork.domain.rule import BusinessRule
from seedwork.domain.value_objects import GenericUUID

EntityId = TypeVar("EntityId", bound=GenericUUID)


@dataclass
class Entity[EntityId: GenericUUID]:
    id: EntityId = field(hash=True)

    @classmethod
    def next_id(cls) -> EntityId:
        return GenericUUID.next_id()


@dataclass(kw_only=True)
class AggregateRoot(Entity[EntityId]):
    """Consists of 1+ entities. Spans transaction boundaries."""

    _events: list = field(default_factory=list)

    @classmethod
    def check_rule(cls, rule: BusinessRule) -> Result[None, BusinessRule]:
        if rule.is_broken():
            return Failure(rule)
        return Success(None)

    def register_event(self, event: DomainEvent):
        self._events.append(event)

    def collect_events(self):
        events = self._events
        self._events = []
        return events
