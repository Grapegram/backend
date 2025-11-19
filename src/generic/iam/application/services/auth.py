from dataclasses import dataclass

from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from src.generic.iam.domain.entities.user import User
from src.generic.iam.domain.repositories.user import UserRepository

from .user_token import LoginTokenStrategy, UserTokenPayload, UserTokenService


@dataclass
class AuthService:
    user_repository: UserRepository
    token_service: UserTokenService

    def _verify_and_parse_token(self, token) -> UserTokenPayload | None:
        token_result = self.token_service.verify(LoginTokenStrategy, token)

        match token_result:
            case Success(payload):
                return payload
            case Failure():
                return None
                # Map token service errors to use case statuses
                # error_name = type(error).__name__
                # if "Expired" in error_name:
                #     state.result = Failure(FailedStatuses.TOKEN_EXPIRED)
                # elif "TokenType" in error_name:
                #     state.result = Failure(FailedStatuses.INVALID_TOKEN_TYPE)
                # else:
                #     state.result = Failure(FailedStatuses.INVALID_TOKEN)
                # raise Exception

    async def auth(self, token: str) -> Result[User, ValueError]:
        payload = self._verify_and_parse_token(token)
        if not payload:
            return Failure(ValueError("Invalid token"))

        user = await self.user_repository.get(payload.user_id)
        if is_successful(user) and user.unwrap().is_active:
            return user

        return Failure(ValueError("Invalid token"))
