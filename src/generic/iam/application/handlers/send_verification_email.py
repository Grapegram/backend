from dataclasses import dataclass

from seedwork.application.handlers import Handler
from src.generic.iam.application.contracts.email import EmailService
from src.generic.iam.application.services.user_token import (
    UserTokenService,
    VerificationTokenPayload,
    VerificationTokenStrategy,
)
from src.generic.iam.domain.events import UserCreated


@dataclass
class SendVerificationEmail(Handler):
    handled = UserCreated

    # Dependencies to be injected
    user_token_service: UserTokenService
    email_service: EmailService

    async def handle(self, event: UserCreated) -> None:
        verification_token = self.user_token_service.create(
            VerificationTokenStrategy,
            VerificationTokenPayload(user_id=str(event.user_id), email=event.email),
        )
        await self.email_service.send_verification_email(
            email=event.email,
            username=event.username,
            token=verification_token,
        )
