from typing import Any, Protocol

from seedwork.handler import Handlable


class Command(Handlable):
    __prefix__ = "command"


class Query(Handlable):
    __prefix__ = "query"


class Handler[T: Handlable](Protocol):
    handled: type[T]

    async def handle(self, handled: T) -> Any: ...

    def __call__(self, handled: T):
        return self.handle(handled)
