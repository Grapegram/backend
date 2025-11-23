from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState

from ...domain.aggregates import User
from ...domain.repositories import UserRepository
from ...domain.value_objects import InvalidPasswordError, Password, WeakPasswordError
from ..services.hasher import HasherService


class FailedStatues(str, Enum):
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    INVALID_CURRENT_PASSWORD = "INVALID_CURRENT_PASSWORD"
    PASSWORD_DUPLICATE = "PASSWORD_DUPLICATE"
    PASSWORD_NOT_STRONG_ENAUGHT = "PASSWORD_NOT_STRONG_ENAUGHT"
    WEEK_PASSWORD = "WEEK_PASSWORD"
    INVALID_PASSWORD = "INVALID_PASSWORD"


@dataclass
class ChangePassword(Story):
    """
    Story for changing a user's password.
    """

    I.find_user
    I.check_account_active
    I.verify_current_password
    I.verify_new_password
    I.hash_new_password
    I.update_password
    I.save_user

    class State(BaseState):
        # input
        user_id: str
        current_password: str
        new_password: str

        # state
        user: User
        new_hashed_password: str

        # result
        result: Result[None, FailedStatues]

    async def find_user(self, state: State):
        user = await self.user_repo.get(state.user_id)
        if user == Nothing:
            state.result = Failure(FailedStatues.USER_NOT_FOUND)
            raise Interrupt
        state.user = user.unwrap()

    def check_account_active(self, state: State):
        if not state.user.is_active:
            state.result = Failure(FailedStatues.ACCOUNT_DEACTIVATED)
            raise Interrupt

    def verify_current_password(self, state: State):
        if not self.hasher_service.verify(
            state.current_password, state.user.hashed_password
        ):
            state.result = Failure(FailedStatues.INVALID_CURRENT_PASSWORD)
            raise Interrupt

    def verify_new_password(self, state: State):
        match Password(state.new_password):
            case Failure(InvalidPasswordError()):
                state.result = Failure(FailedStatues.INVALID_PASSWORD)
                raise Interrupt
            case Failure(WeakPasswordError()):
                state.result = Failure(FailedStatues.WEEK_PASSWORD)
                raise Interrupt

    def hash_new_password(self, state: State):
        state.new_hashed_password = self.hasher_service.hash(state.new_password)

    def update_password(self, state: State):
        state.user.change_password(state.new_hashed_password)

    async def save_user(self, state: State):
        await self.user_repo.save(state.user)
        state.result = Success(None)

    # Dependencies to be injected
    user_repo: UserRepository
    hasher_service: HasherService
