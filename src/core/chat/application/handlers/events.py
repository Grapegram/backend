from dataclasses import asdict, dataclass

from seedwork.application.handlers import Handler
from seedwork.application.notifier import Notifier
from seedwork.application.object_storage import ObjectStorage
from src.core.chat.domain.events.chat_events import MemberAdded
from src.core.chat.domain.events.message_events import MessageDeleted, MessageSent


@dataclass
class ExposeMessageSentEvent(Handler):
    handled = MessageSent

    # Dependencies to be injected
    notifier: Notifier
    object_storage: ObjectStorage

    async def handle(self, event: MessageSent) -> None:
        images = [
            await self.object_storage.get_file_url(key=image_key)
            for image_key in event.images
        ]
        prepared_message = asdict(event)
        prepared_message["images"] = images
        await self.notifier.notify(
            f"chat-{event.chat_id}",
            {
                "event_type": "message_sent",
                "data": prepared_message,
            },
        )


@dataclass
class ExposeMessageDeletedEvent(Handler):
    handled = MessageDeleted

    # Dependencies to be injected
    notifier: Notifier

    async def handle(self, event: MessageDeleted) -> None:
        await self.notifier.notify(
            f"chat-{event.chat_id}",
            {
                "event_type": "message_deleted",
                "data": asdict(event),
            },
        )


@dataclass
class ExposeMemberAddedEvent(Handler):
    handled = MemberAdded

    # Dependencies to be injected
    notifier: Notifier

    async def handle(self, event: MemberAdded) -> None:
        await self.notifier.notify(
            f"chat-{event.chat_id}",
            {
                "event_type": "member_added",
                "data": asdict(event),
            },
        )
