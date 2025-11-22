from dataclasses import dataclass, field
from typing import Protocol

from seedwork.application.handlers import Handler


@dataclass
class EventBusRouter:
    handlers: list[type[Handler]] = field(default_factory=list)

    def register(self, handler: type[Handler]):
        self.handlers.append(handler)


class EventBus(Protocol):
    def include_router(self, route: EventBusRouter) -> None: ...
    def include_routes(self, routes: list[EventBusRouter]) -> None:
        for route in routes:
            self.include_router(route)

    async def publish(self, event: object) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
