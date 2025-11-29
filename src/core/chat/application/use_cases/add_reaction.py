from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Message
from ...domain.events import MessageReactionAdded
from ...domain.repositories import MessageRepository


class FailedStatuses(str, Enum):
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    MESSAGE_DELETED = "MESSAGE_DELETED"
    INVALID_REACTION = "INVALID_REACTION"


@dataclass
class AddReaction(Story):
    """
    Story for adding a reaction to a message.
    """

    I.find_message
    I.check_not_deleted
    I.add_reaction
    I.save_message
    I.publish_events

    class State(BaseState):
        # input
        message_id: str
        user_id: str
        reaction: str

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

    def check_not_deleted(self, state: State):
        if state.message.is_deleted:
            state.result = Failure(FailedStatuses.MESSAGE_DELETED)
            raise Interrupt

    def add_reaction(self, state: State):
        try:
            state.message.add_reaction(state.user_id, state.reaction)
        except ValueError:
            state.result = Failure(FailedStatuses.INVALID_REACTION)
            raise Interrupt

    async def save_message(self, state: State):
        await self.message_repo.save(state.message)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(
            state.message.collect_events(), (MessageReactionAdded,)
        ):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    message_repo: MessageRepository
    event_bus: EventBus
