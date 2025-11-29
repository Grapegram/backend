from dataclasses import dataclass

from returns.result import Success

from src.core.chat.application.contracts.auth import AuthService
from src.generic.iam.application.services.auth import AuthService as IAMAuthService


@dataclass
class IAMAuthServiceACL(AuthService):
    iam_auth: IAMAuthService

    async def auth(self, token: str) -> str | None:
        res = await self.iam_auth.auth(token)
        match res:
            case Success(user):
                return str(user.id)
        return None
