from dataclasses import dataclass

from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.redis import RedisBroker, RedisRouter

from seedwork.application.handlers import Handler
from seedwork.domain.events import DomainEvent

from ..application.event_bus import EventBus, EventBusRouter


def register_handler(router: RedisRouter, handler: Handler):
    async def fs_handler(event: str, handler_):
        await handler_(event)

    fs_handler.__annotations__ = {"event": handler.handled, "handler_": FromDishka[handler]}
    router.subscriber(handler.handled.__tag__)(inject(fs_handler))


@dataclass
class FastStreamEventBus(EventBus):
    publisher: RedisBroker

    def include_router(self, route: EventBusRouter):
        router = RedisRouter()
        for handler in route.handlers:
            register_handler(router, handler)
        self.publisher.include_router(router)

    async def publish(self, event: DomainEvent):
        await self.publisher.publish(event, event.__tag__)

    async def start(self):
        await self.publisher.start()

    async def stop(self):
        await self.publisher.stop()
