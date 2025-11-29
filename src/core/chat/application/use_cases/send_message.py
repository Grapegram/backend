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


class FailedStatuses(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"


@dataclass
class SendMessage(Story):
    """
    Story for sending a message in a chat.
    """

    I.create_message
    I.save_message
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        sender_id: str
        text: str

        # state
        message: Message

        # result
        result: Result[Message, FailedStatuses]

    async def create_message(self, state: State):
        message = Message.create(
            chat_id=state.chat_id,
            sender_id=state.sender_id,
            text=state.text,
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
    event_bus: EventBus
