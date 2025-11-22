from seedwork.handler import Handlable


class DomainEvent(Handlable):
    """
    Domain events are used to communicate between aggregates within a single transaction boundary via in-memory queue.
    Domain events are synchronous in nature.
    """

    __prefix__ = "domain_event"

    def __next__(self):
        yield self


class CompositeDomainEvent(DomainEvent):
    events: list[DomainEvent]

    def __next__(self):
        yield from self.events


def filter_events(
    enents,
    allowed_events: tuple[type[DomainEvent]],
):
    for event in enents:
        if isinstance(event, allowed_events):
            yield event
