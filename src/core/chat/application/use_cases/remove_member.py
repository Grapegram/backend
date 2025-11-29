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
from ...domain.events import MemberRemoved
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    ACTOR_NOT_MEMBER = "ACTOR_NOT_MEMBER"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    CANNOT_REMOVE_OWNER = "CANNOT_REMOVE_OWNER"
    MUST_HAVE_ONE_MEMBER = "MUST_HAVE_ONE_MEMBER"


@dataclass
class RemoveMember(Story):
    """
    Story for removing a member from a chat.
    """

    I.find_chat
    I.remove_member_from_chat
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        user_id: str
        removed_by: str

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

    async def remove_member_from_chat(self, state: State):
        result = state.chat.remove_member(
            user_id=state.user_id,
            removed_by=state.removed_by,
        )
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "not a member" in error_msg and state.removed_by in error_msg:
                state.result = Failure(FailedStatuses.ACTOR_NOT_MEMBER)
            elif "not a member" in error_msg:
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            elif "Only admin" in error_msg:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            elif "Cannot remove owner" in error_msg or "owner" in error_msg.lower():
                state.result = Failure(FailedStatuses.CANNOT_REMOVE_OWNER)
            elif "at least one member" in error_msg:
                state.result = Failure(FailedStatuses.MUST_HAVE_ONE_MEMBER)
            else:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            raise Interrupt

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (MemberRemoved,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
