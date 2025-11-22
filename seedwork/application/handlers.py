from abc import ABC
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Concatenate

from seedwork.domain.events import DomainEvent


@dataclass(frozen=True)
class Message(ABC): ...


class Command(Message): ...


class Query(Message): ...


type Handlable = Message | DomainEvent
type HandlerFunction[T = Any] = Callable[Concatenate[Handlable, ...], Awaitable[T]]


class Handler[T: Handlable]:
    handled: T
    handler: HandlerFunction[T]

    def __init__(self, handled: T, handler: HandlerFunction[T]):
        self.handled = handled
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


def handle[T: Handlable](handled: T) -> Callable[[HandlerFunction[T]], Handler[T]]:
    return lambda handler: Handler(handled, handler)
