from seedwork.application.event_bus import EventBusRouter

from ..application.handlers import SendVerificationEmail

routes = [EventBusRouter([SendVerificationEmail])]
__all__ = ["routes"]
