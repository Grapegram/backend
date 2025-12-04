from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState

from ...domain.aggregates import Chat
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    CANNOT_CREATE_CHAT_WITH_SELF = "CANNOT_CREATE_CHAT_WITH_SELF"
    CHAT_ALREADY_EXISTS = "CHAT_ALREADY_EXISTS"


@dataclass
class CreateDirectChat(Story):
    """
    Story for creating a direct chat between two users.
    Ensures idempotency - only one direct chat exists between two users.
    """

    I.check_chat_does_not_exists
    I.create
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        user1_id: str
        user2_id: str

        # state
        chat: Chat

        # result
        result: Result[Chat, FailedStatuses]

    async def check_chat_does_not_exists(self, state: State):
        existing = await self.chat_repo.get_direct_chat_between(
            state.user1_id,
            state.user2_id,
        )
        if existing != Nothing:
            state.result = Failure(FailedStatuses.CHAT_ALREADY_EXISTS)
            state.chat = existing.unwrap()
            raise Interrupt

    async def create(self, state: State):
        chat = Chat.create_direct_chat(
            user1_id=state.user1_id,
            user2_id=state.user2_id,
        )
        if not is_successful(chat):
            state.result = Failure(FailedStatuses.INVALID_INPUT)
            raise Interrupt
        state.chat = chat.unwrap()

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(state.chat)

    async def publish_events(self, state: State):
        await self.event_bus.publish(*state.chat.collect_events())

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
