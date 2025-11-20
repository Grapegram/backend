from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from seedwork.stories import I, Interrupt, Story
from seedwork.stories import State as BaseState

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ..services.email import EmailService
from ..services.hasher import HasherService
from ..services.user_token import UserTokenService, VerificationTokenStrategy


class FailedStatuses(str, Enum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"


@dataclass
class Registeration(Story):
    """
    Story for registering a new user in the system.
    """

    I.check_email_uniqueness
    I.check_username_uniqueness
    I.hash_password
    I.create_user
    I.save_user
    I.send_verification_email

    class State(BaseState):
        # input
        email: str
        username: str
        password: str

        # state
        hashed_password: str
        user: User
        verification_token: str

        # result
        result: Result[None, FailedStatuses]

    async def check_email_uniqueness(self, state: State):
        existing_user = await self.user_repo.get_by_email(state.email)
        if existing_user != Nothing:
            state.result = Failure(FailedStatuses.EMAIL_ALREADY_EXISTS)
            raise Interrupt

    async def check_username_uniqueness(self, state: State):
        existing_user = await self.user_repo.get_by_username(state.username)
        if existing_user != Nothing:
            state.result = Failure(FailedStatuses.USERNAME_ALREADY_EXISTS)
            raise Interrupt

    async def hash_password(self, state: State):
        state.hashed_password = self.hasher_service.hash(state.password)

    async def create_user(self, state: State):
        user = User.create(
            email=state.email,
            username=state.username,
            hashed_password=state.hashed_password,
        )
        if not is_successful(user):
            state.result = Failure(FailedStatuses.INVALID_CREDENTIALS)
            raise Interrupt
        state.user = user.unwrap()

    async def save_user(self, state: State):
        await self.user_repo.save(state.user)
        state.result = Success(None)

    async def send_verification_email(self, state: State):
        state.verification_token = self.user_token_service.create(
            VerificationTokenStrategy, state.user
        )
        await self.email_service.send_verification_email(
            email=str(state.user.email),
            username=state.user.username,
            token=state.verification_token,
        )

    # Dependencies to be injected
    user_repo: UserRepository
    hasher_service: HasherService
    user_token_service: UserTokenService
    email_service: EmailService
