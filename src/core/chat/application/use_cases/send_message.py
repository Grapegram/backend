from dataclasses import dataclass
from enum import Enum

from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Message
from ...domain.events import MessageSent
from ...domain.repositories import MessageRepository
from ..services.message import MessageService


class FailedStatuses(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    UPLOAD_FAILED = "UPLOAD_FAILED"


@dataclass
class SendMessage(Story):
    """
    Story for sending a message in a chat with optional image attachments.
    """

    I.upload_images
    I.create_message
    I.save_message
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        sender_id: str
        text: str | None = None
        image_files: list[tuple[bytes, str]] | None = (
            None  # list of (data, content_type)
        )

        # state
        message: Message
        image_keys: list[str] | None = None

        # result
        result: Result[Message, FailedStatuses]

    async def upload_images(self, state: State):
        print("IMG", state.image_files)
        if not state.image_files:
            state.image_keys = []
            return

        try:
            state.image_keys = await self.message_service.upload_images(
                state.image_files
            )
        except Exception:
            state.result = Failure(FailedStatuses.UPLOAD_FAILED)
            raise Interrupt

    async def create_message(self, state: State):
        message = Message.create(
            chat_id=state.chat_id,
            sender_id=state.sender_id,
            text=state.text,
            images=state.image_keys,
        )
        if not is_successful(message):
            state.result = Failure(FailedStatuses.INVALID_INPUT)
            raise Interrupt
        state.message = message.unwrap()

    async def save_message(self, state: State):
        await self.message_repo.save(state.message)
        state.result = Success(state.message)

    async def publish_events(self, state: State):
        for event in filter_events(state.message.collect_events(), (MessageSent,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    message_repo: MessageRepository
    message_service: MessageService
    event_bus: EventBus
