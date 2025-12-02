from dataclasses import asdict, dataclass

from seedwork.application.handlers import Handler
from seedwork.application.notifier import Notifier
from seedwork.application.object_storage import ObjectStorage
from src.core.chat.domain.events.message_events import MessageSent


@dataclass
class ExposeMessageSentEvent(Handler):
    handled = MessageSent

    # Dependencies to be injected
    notifier: Notifier
    object_storage: ObjectStorage

    async def handle(self, event: MessageSent) -> None:
        images = [
            await self.object_storage.get_file_url(key=image_key)
            for image_key in event.image_keys
        ]
        exposed = asdict(event)
        exposed["images"] = images
        await self.notifier.notify(f"chat-{event.chat_id}", exposed)
