from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Message
from ...domain.events import MessageEdited
from ...domain.repositories import MessageRepository


class FailedStatuses(str, Enum):
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    ONLY_AUTHOR_CAN_EDIT = "ONLY_AUTHOR_CAN_EDIT"
    MESSAGE_DELETED = "MESSAGE_DELETED"
    TEXT_UNCHANGED = "TEXT_UNCHANGED"
    INVALID_TEXT = "INVALID_TEXT"


@dataclass
class EditMessage(Story):
    """
    Story for editing a message.
    """

    I.find_message
    I.edit_message_text
    I.save_message
    I.publish_events

    class State(BaseState):
        # input
        message_id: str
        new_text: str
        editor_id: str

        # state
        message: Message

        # result
        result: Result[None, FailedStatuses]

    async def find_message(self, state: State):
        message = await self.message_repo.get(state.message_id)
        if message == Nothing:
            state.result = Failure(FailedStatuses.MESSAGE_NOT_FOUND)
            raise Interrupt
        state.message = message

    async def edit_message_text(self, state: State):
        result = state.message.edit_text(state.new_text, state.editor_id)
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "Only author" in error_msg or "author" in error_msg.lower():
                state.result = Failure(FailedStatuses.ONLY_AUTHOR_CAN_EDIT)
            elif "deleted" in error_msg.lower():
                state.result = Failure(FailedStatuses.MESSAGE_DELETED)
            elif "different" in error_msg.lower():
                state.result = Failure(FailedStatuses.TEXT_UNCHANGED)
            else:
                state.result = Failure(FailedStatuses.INVALID_TEXT)
            raise Interrupt

    async def save_message(self, state: State):
        await self.message_repo.save(state.message)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.message.collect_events(), (MessageEdited,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    message_repo: MessageRepository
    event_bus: EventBus
