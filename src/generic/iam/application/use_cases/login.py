from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState

from ...domain.aggregates import User
from ...domain.repositories import UserRepository
from ..services.hasher import HasherService
from ..services.user_token import LoginTokenStrategy, UserTokenService


class FailedStatuses(str, Enum):
    MISSING_CREDENTIAL = "MISSING_CREDENTIAL"
    MISSING_PASSWORD = "MISSING_PASSWORD"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
    ACCOUNT_NOT_VERIFIED = "ACCOUNT_NOT_VERIFIED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"


@dataclass
class AuthToken:
    access_token: str


@dataclass
class Login(Story):
    """
    Story for authenticating a user and creating a session.
    """

    I.find_user
    I.check_account_active
    I.verify_password
    I.check_account_verified
    I.record_login
    I.save_user
    I.generate_auth_token

    class State(BaseState):
        # input
        credential: str
        password: str

        # state
        user: User

        # result
        result: Result[AuthToken, FailedStatuses]

    async def find_user(self, state: State):
        # Try to find by email first, then by username
        user = await self.user_repo.get_by_email(state.credential)
        if user == Nothing:
            user = await self.user_repo.get_by_username(state.credential)
        if user == Nothing:
            state.result = Failure(FailedStatuses.USER_NOT_FOUND)
            raise Interrupt
        state.user = user.unwrap()

    async def check_account_active(self, state: State):
        if not state.user.is_active:
            state.result = Failure(FailedStatuses.ACCOUNT_DEACTIVATED)
            raise Interrupt

    async def verify_password(self, state: State):
        if not self.hasher_service.verify(state.password, state.user.hashed_password):
            state.result = Failure(FailedStatuses.INVALID_CREDENTIALS)
            raise Interrupt

    async def check_account_verified(self, state: State):
        print("ACCOUNT_NOT_VERIFIED!!!")
        if not state.user.is_verified:
            state.result = Failure(FailedStatuses.ACCOUNT_NOT_VERIFIED)
            raise Interrupt

    async def record_login(self, state: State):
        state.user.record_login()

    async def save_user(self, state: State):
        await self.user_repo.save(state.user)

    async def generate_auth_token(self, state: State):
        auth_token = self.user_token_service.create(LoginTokenStrategy, state.user)
        state.result = Success(AuthToken(access_token=auth_token))

    # Dependencies to be injected
    user_repo: UserRepository
    hasher_service: HasherService
    user_token_service: UserTokenService
