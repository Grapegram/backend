from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events

from ...domain.aggregates import Chat, Message
from ...domain.entities import Member
from ...domain.events import MessageDeleted
from ...domain.repositories import ChatRepository, MessageRepository


class FailedStatuses(str, Enum):
    MESSAGE_NOT_FOUND = "MESSAGE_NOT_FOUND"
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ALREADY_DELETED = "ALREADY_DELETED"


@dataclass
class DeleteMessage(Story):
    """
    Story for deleting a message.
    """

    I.find_message
    I.check_not_deleted
    I.find_chat
    I.get_deleter_member
    I.delete_message
    I.save_message
    I.publish_events

    class State(BaseState):
        # input
        message_id: str
        deleter_id: str

        # state
        message: Message
        chat: Chat
        deleter: Member

        # result
        result: Result[None, FailedStatuses]

    async def find_message(self, state: State):
        message = await self.message_repo.get(state.message_id)
        if message == Nothing:
            state.result = Failure(FailedStatuses.MESSAGE_NOT_FOUND)
            raise Interrupt
        state.message = message

    def check_not_deleted(self, state: State):
        if state.message.is_deleted:
            state.result = Failure(FailedStatuses.ALREADY_DELETED)
            raise Interrupt

    async def find_chat(self, state: State):
        chat = await self.chat_repo.get(str(state.message.chat_id))
        if chat == Nothing:
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.chat = chat

    def get_deleter_member(self, state: State):
        deleter = state.chat.get_member(state.deleter_id)
        if not deleter:
            state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            raise Interrupt
        state.deleter = deleter

    async def delete_message(self, state: State):
        result = state.message.delete(state.deleter)
        if not is_successful(result):
            error = result.failure()
            error_msg = str(error)
            if "admin" in error_msg.lower() or "author" in error_msg.lower():
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            else:
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            raise Interrupt

    async def save_message(self, state: State):
        await self.message_repo.save(state.message)
        state.result = Success(None)

    async def publish_events(self, state: State):
        for event in filter_events(state.message.collect_events(), (MessageDeleted,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    message_repo: MessageRepository
    chat_repo: ChatRepository
    event_bus: EventBus
