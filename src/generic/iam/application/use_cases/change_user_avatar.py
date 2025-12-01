from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.event_bus import EventBus
from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState
from seedwork.domain.events import filter_events
from src.generic.iam.application.services.user import UserService

from ...domain.aggregates import User
from ...domain.events import UserAvatarChanged
from ...domain.repositories import UserRepository


class FailedStatuses(str, Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    UPLOAD_FAILED = "UPLOAD_FAILED"


@dataclass
class ChangeUserAvatar(Story):
    """
    Story for changing a user's avatar.

    This use case handles uploading an image to object storage
    and updating the user aggregate with the new avatar URL.
    """

    I.find_user
    I.upload_avatar
    I.change_avatar
    I.save_user
    I.publish_events

    class State(BaseState):
        # input
        user_id: str
        image_data: bytes | None
        content_type: str | None

        # state
        user: User
        avatar: str | None
        avatar_url: str | None

        # result
        result: Result[str | None, FailedStatuses]

    async def find_user(self, state: State):
        user = await self.user_repo.get(state.user_id)
        if user == Nothing:
            state.result = Failure(FailedStatuses.USER_NOT_FOUND)
            raise Interrupt
        state.user = user.unwrap()

    async def upload_avatar(self, state: State):
        if state.image_data is None:
            # Removing avatar
            state.avatar = None
            return

        try:
            key, url = await self.user_service.upload_avatar(
                state.user, state.content_type, state.image_data
            )
            state.avatar = key
            state.avatar_url = url
        except Exception:
            state.result = Failure(FailedStatuses.UPLOAD_FAILED)
            raise Interrupt

    async def change_avatar(self, state: State):
        state.user.change_avatar(state.avatar)

    async def save_user(self, state: State):
        await self.user_repo.save(state.user)
        state.result = Success(state.avatar_url)

    async def publish_events(self, state: State):
        for event in filter_events(state.user.collect_events(), (UserAvatarChanged,)):
            await self.event_bus.publish(event)

    # Dependencies to be injected
    user_repo: UserRepository
    user_service: UserService
    event_bus: EventBus
