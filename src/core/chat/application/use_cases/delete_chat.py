from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Chat
from ...domain.events import ChatDeleted
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"


@dataclass
class DeleteChat(Story):
    """
    Story for deleting a chat.
    """

    I.find_chat
    I.delete_chat
    I.remove_from_repository
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        deleted_by: str

        # state
        chat: Chat

        # result
        result: Result[None, FailedStatuses]

    async def find_chat(self, state: State):
        chat = await self.chat_repo.get(state.chat_id)
        if chat == Nothing:
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.chat = chat.unwrap()

    async def delete_chat(self, state: State):
        result = state.chat.delete(state.deleted_by)
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "not a member" in error_msg.lower():
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            else:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            raise Interrupt

    async def remove_from_repository(self, state: State):
        result = await self.chat_repo.delete(state.chat_id)
        if not is_successful(result):
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (ChatDeleted,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
