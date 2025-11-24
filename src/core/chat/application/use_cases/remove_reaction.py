from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Message
from ...domain.events import MessageReactionRemoved
from ...domain.repositories import MessageRepository


class FailedStatuses(str, Enum):
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    REACTION_NOT_FOUND = "REACTION_NOT_FOUND"


@dataclass
class RemoveReaction(Story):
    """
    Story for removing a reaction from a message.
    """

    I.find_message
    I.remove_reaction
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

    def remove_reaction(self, state: State):
        state.message.remove_reaction(state.user_id, state.reaction)

    async def save_message(self, state: State):
        await self.message_repo.save(state.message)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(
            state.message.collect_events(), (MessageReactionRemoved,)
        ):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    message_repo: MessageRepository
    event_bus: EventBus
