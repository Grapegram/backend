from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Chat
from ...domain.events import ChatUnarchived
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    NOT_ARCHIVED = "NOT_ARCHIVED"


@dataclass
class UnarchiveChat(Story):
    """
    Story for unarchiving a chat.
    """

    I.find_chat
    I.check_is_archived
    I.unarchive_chat
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        unarchived_by: str

        # state
        chat: Chat

        # result
        result: Result[None, FailedStatuses]

    async def find_chat(self, state: State):
        chat = await self.chat_repo.get(state.chat_id)
        if chat == Nothing:
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.chat = chat

    def check_is_archived(self, state: State):
        if not state.chat.is_archived:
            state.result = Failure(FailedStatuses.NOT_ARCHIVED)
            raise Interrupt

    def unarchive_chat(self, state: State):
        try:
            state.chat.unarchive(state.unarchived_by)
        except ValueError as e:
            error_msg = str(e)
            if "not a member" in error_msg:
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            else:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            raise Interrupt

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (ChatUnarchived,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
