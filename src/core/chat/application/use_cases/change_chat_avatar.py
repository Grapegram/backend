from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events
from src.core.chat.application.services.chat import ChatService

from ...domain.aggregates import Chat
from ...domain.events import ChatAvatarChanged
from ...domain.repositories import ChatRepository


class FailedStatuses(str, Enum):
    CHAT_NOT_FOUND = "CHAT_NOT_FOUND"
    USER_NOT_MEMBER = "USER_NOT_MEMBER"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    INVALID_AVATAR_URL = "INVALID_AVATAR_URL"
    UPLOAD_FAILED = "UPLOAD_FAILED"


@dataclass
class ChangeChatAvatar(Story):
    """
    Story for changing a chat's avatar.

    This use case handles uploading an image to object storage
    and updating the chat aggregate with the new avatar URL.
    """

    I.find_chat
    I.upload_avatar
    I.change_avatar
    I.save_chat
    I.publish_events

    class State(BaseState):
        # input
        chat_id: str
        changed_by: str
        image_data: bytes | None
        content_type: str | None

        # state
        chat: Chat
        avatar: str | None
        avatar_url: str | None

        # result
        result: Result[str | None, FailedStatuses]

    async def find_chat(self, state: State):
        chat = await self.chat_repo.get(state.chat_id)
        if chat == Nothing:
            state.result = Failure(FailedStatuses.CHAT_NOT_FOUND)
            raise Interrupt
        state.chat = chat

    async def upload_avatar(self, state: State):
        if state.image_data is None:
            # Removing avatar
            state.avatar = None
            return

        try:
            key, url = await self.chat_service.upload_avatar(
                state.chat, state.content_type, state.image_data
            )
            state.avatar = key
            state.avatar_url = url
        except Exception:
            state.result = Failure(FailedStatuses.UPLOAD_FAILED)
            raise Interrupt

    async def change_avatar(self, state: State):
        result = state.chat.change_avatar(state.avatar, state.changed_by)
        if not is_successful(result):
            error = result.failure()
            if "not a member" in str(error):
                state.result = Failure(FailedStatuses.USER_NOT_MEMBER)
            elif "Only admin" in str(error):
                state.result = Failure(FailedStatuses.INSUFFICIENT_PERMISSIONS)
            else:
                state.result = Failure(FailedStatuses.INVALID_AVATAR_URL)
            raise Interrupt

    async def save_chat(self, state: State):
        await self.chat_repo.save(state.chat)
        state.result = Success(state.avatar)

    async def publish_events(self, state: State):
        for event in filter_events(state.chat.collect_events(), (ChatAvatarChanged,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    chat_repo: ChatRepository
    chat_service: ChatService
    event_bus: EventBus
