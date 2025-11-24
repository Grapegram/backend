from dataclasses import dataclass
from enum import Enum

from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Chat
from ...domain.events import ChatCreated
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    USER_NOT_FOUND = "USER_NOT_FOUND"


@dataclass
class CreateChat(Story):
    """
    Story for creating a new chat.
    """

    I.create_chat
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        title: str
        created_by: str

        # state
        chat: Chat

        # result
        result: Result[Chat, FailedStatuses]

    async def create_chat(self, state: State):
        chat = Chat.create(
            title=state.title,
            created_by=state.created_by,
        )
        if not is_successful(chat):
            state.result = Failure(FailedStatuses.INVALID_INPUT)
            raise Interrupt
        state.chat = chat.unwrap()

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(state.chat)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (ChatCreated,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
