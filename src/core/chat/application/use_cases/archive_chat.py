from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Chat
from ...domain.events import ChatArchived
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ALREADY_ARCHIVED = "ALREADY_ARCHIVED"


@dataclass
class ArchiveChat(Story):
    """
    Story for archiving a chat.
    """

    I.find_chat
    I.check_not_archived
    I.archive_chat
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        archived_by: str

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

    def check_not_archived(self, state: State):
        if state.chat.is_archived:
            state.result = Failure(FailedStatuses.ALREADY_ARCHIVED)
            raise Interrupt

    def archive_chat(self, state: State):
        try:
            state.chat.archive(state.archived_by)
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
        for event in filter_events(state.chat.collect_events(), (ChatArchived,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
