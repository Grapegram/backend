from dataclasses import dataclass
from enum import Enum

from returns.maybe import Nothing
from returns.result import Failure, Result, Success

from seedwork.application.stories import I, Interrupt, Story
from seedwork.application.stories import State as BaseState

from ...domain.aggregates import User
from ...domain.repositories import UserRepository
from ..services.user_token import UserTokenService, VerificationTokenStrategy


class FailedStatuses(str, Enum):
    MISSING_TOKEN = "MISSING_TOKEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN_TYPE = "INVALID_TOKEN_TYPE"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    ALREADY_VERIFIED = "ALREADY_VERIFIED"


@dataclass
class VerifyEmail(Story):
    """
    Story for verifying a user's email address via token.
    """

    I.verify_and_parse_token
    I.find_user
    I.check_not_already_verified
    I.mark_as_verified
    I.save_user

    class State(BaseState):
        # input
        verification_token: str

        # state
        user_id: str
        user: User

        # result
        result: Result[None, FailedStatuses]

    def verify_and_parse_token(self, state: State):
        token_result = self.user_token_service.verify(
            VerificationTokenStrategy, state.verification_token
        )

        match token_result:
            case Success(payload):
                state.user_id = payload.user_id
            case Failure(error):
                # Map token service errors to use case statuses
                error_name = type(error).__name__
                if "Expired" in error_name:
                    state.result = Failure(FailedStatuses.TOKEN_EXPIRED)
                elif "TokenType" in error_name:
                    state.result = Failure(FailedStatuses.INVALID_TOKEN_TYPE)
                else:
                    state.result = Failure(FailedStatuses.INVALID_TOKEN)
                raise Interrupt

    async def find_user(self, state: State):
        user = await self.user_repo.get(state.user_id)
        if user == Nothing:
            state.result = Failure(FailedStatuses.USER_NOT_FOUND)
            raise Interrupt
        state.user = user.unwrap()

    def check_not_already_verified(self, state: State):
        if state.user.is_verified:
            state.result = Failure(FailedStatuses.ALREADY_VERIFIED)
            raise Interrupt

    def mark_as_verified(self, state: State):
        state.user.verify_email()

    async def save_user(self, state: State):
        await self.user_repo.save(state.user)
        state.result = Success(None)

    # Dependencies to be injected
    user_token_service: UserTokenService
    user_repo: UserRepository
