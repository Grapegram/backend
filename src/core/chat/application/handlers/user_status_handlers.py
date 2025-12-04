"""
User Status Event Handlers

Handlers for user status events that update Redis and broadcast notifications.
"""

from dataclasses import dataclass

from seedwork.application.handlers import Handler
from seedwork.application.notifier import Notifier
from src.core.chat.application.contracts.user_status import UserStatusService
from src.core.chat.application.events import (
    UserOffline,
    UserOnline,
    UserTypingStarted,
    UserTypingStopped,
)


@dataclass
class HandleUserOnline(Handler):
    handled = UserOnline

    user_status_service: UserStatusService
    notifier: Notifier

    async def handle(self, event: UserOnline) -> None:
        await self.user_status_service.mark_online(event.user_id, event.device_id)
        await self.notifier.notify(
            "chat-events",
            {
                "event_type": "user_online",
                "data": {
                    "user_id": event.user_id,
                },
            },
        )


@dataclass
class HandleUserOffline(Handler):
    handled = UserOffline

    user_status_service: UserStatusService
    notifier: Notifier

    async def handle(self, event: UserOffline) -> None:
        await self.user_status_service.mark_offline(event.user_id, event.device_id)
        await self.notifier.notify(
            "chat-events",
            {
                "event_type": "user_offline",
                "data": {
                    "user_id": event.user_id,
                },
            },
        )


@dataclass
class HandleUserTypingStarted(Handler):
    handled = UserTypingStarted

    user_status_service: UserStatusService
    notifier: Notifier

    async def handle(self, event: UserTypingStarted) -> None:
        await self.user_status_service.start_typing(event.user_id, event.chat_id)
        await self.notifier.notify(
            f"chat-{event.chat_id}",
            {
                "event_type": "user_typing_started",
                "data": {
                    "user_id": event.user_id,
                    "chat_id": event.chat_id,
                },
            },
        )


@dataclass
class HandleUserTypingStopped(Handler):
    handled = UserTypingStopped

    user_status_service: UserStatusService
    notifier: Notifier

    async def handle(self, event: UserTypingStopped) -> None:
        await self.user_status_service.stop_typing(event.user_id, event.chat_id)
        await self.notifier.notify(
            f"chat-{event.chat_id}",
            {
                "event_type": "user_typing_stopped",
                "data": {
                    "user_id": event.user_id,
                    "chat_id": event.chat_id,
                },
            },
        )
