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
from ...domain.events import ChatTitleChanged
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_TITLE = "INVALID_TITLE"


@dataclass
class ChangeChatTitle(Story):
    """
    Story for changing a chat's title.
    """

    I.find_chat
    I.change_title
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        new_title: str
        changed_by: str

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

    async def change_title(self, state: State):
        result = state.chat.change_title(state.new_title, state.changed_by)
        if not is_successful(result):
            error = result.failure()
            if "not a member" in str(error):
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            elif "Only admin" in str(error):
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            else:
                state.result = Failure(FailedStatuses.INVALID_TITLE)
            raise Interrupt

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (ChatTitleChanged,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
