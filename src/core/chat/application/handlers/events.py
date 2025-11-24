from dataclasses import asdict, dataclass

from seedwork.application.handlers import Handler
from seedwork.application.notifier import Notifier
from src.core.chat.domain.events.message_events import MessageSent


@dataclass
class ExposeMessageSentEvent(Handler):
    handled = MessageSent

    # Dependencies to be injected
    notifier: Notifier

    async def handle(self, event: MessageSent) -> None:
        await self.notifier.notify(f"chat-{event.chat_id}", asdict(event))
