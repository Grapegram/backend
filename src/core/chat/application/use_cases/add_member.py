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
from ...domain.entities import Member, MemberRole
from ...domain.events import MemberAdded
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    ACTOR_NOT_MEMBER = "ACTOR_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    MEMBER_ALREADY_EXISTS = "MEMBER_ALREADY_EXISTS"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass
class AddMember(Story):
    """
    Story for adding a member to a chat.
    """

    I.find_chat
    I.add_member_to_chat
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        user_id: str
        added_by: str
        role: MemberRole = MemberRole.MEMBER

        # state
        chat: Chat
        member: Member

        # result
        result: Result[Member, FailedStatuses]

    async def find_chat(self, state: State):
        chat = await self.chat_repo.get(state.chat_id)
        if chat == Nothing:
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.chat = chat.unwrap()

    async def add_member_to_chat(self, state: State):
        result = state.chat.add_member(
            user_id=state.user_id,
            added_by=state.added_by,
            role=state.role,
        )
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "not a member" in error_msg:
                state.result = Failure(FailedStatuses.ACTOR_NOT_MEMBER)
            elif "Only admin" in error_msg:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            elif "already a member" in error_msg:
                state.result = Failure(FailedStatuses.MEMBER_ALREADY_EXISTS)
            else:
                state.result = Failure(FailedStatuses.INVALID_INPUT)
            raise Interrupt
        state.member = result.unwrap()

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(state.member)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (MemberAdded,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    event_bus: EventBus
