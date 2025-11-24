from seedwork.application.event_bus import EventBusRouter

from ..application.handlers import handlers

routes = [EventBusRouter(handlers)]
__all__ = ["routes"]
