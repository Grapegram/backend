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
from ...domain.entities import MemberRole
from ...domain.events import MemberRoleChanged
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    ACTOR_NOT_MEMBER = "ACTOR_NOT_MEMBER"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ONLY_OWNER_CAN_CHANGE_OWNERSHIP = "ONLY_OWNER_CAN_CHANGE_OWNERSHIP"


@dataclass
class ChangeMemberRole(Story):
    """
    Story for changing a member's role in a chat.
    """

    I.find_chat
    I.change_role
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        user_id: str
        new_role: MemberRole
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

    async def change_role(self, state: State):
        result = state.chat.change_member_role(
            user_id=state.user_id,
            new_role=state.new_role,
            changed_by=state.changed_by,
        )
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "not a member" in error_msg and state.changed_by in error_msg:
                state.result = Failure(FailedStatuses.ACTOR_NOT_MEMBER)
            elif "not a member" in error_msg:
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            elif "Only owner" in error_msg or "ownership" in error_msg.lower():
                state.result = Failure(FailedStatuses.ONLY_OWNER_CAN_CHANGE_OWNERSHIP)
            else:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            raise Interrupt

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (MemberRoleChanged,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
