from dishka import Provider, Scope, provide

from src.generic.iam.application.services.email import EmailService
from src.generic.iam.application.services.hasher import HasherService
from src.generic.iam.application.services.token import TokenService
from src.generic.iam.application.services.user_token import UserTokenService
from src.generic.iam.application.use_cases.login import Login
from src.generic.iam.application.use_cases.registration import Registeration
from src.generic.iam.domain.repositories.user import UserRepository
from src.generic.iam.infrastracture.repositories import (
    InMemoryUserRepository,
)
from src.generic.iam.infrastracture.services import (
    BCryptHasherService,
    JWTTokenService,
    SMTPEmailService,
)

from ..settings import IAMSettings


class IAMProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_hasher_service(self, settings: IAMSettings) -> HasherService:
        return BCryptHasherService(
            salt=settings.password_salt,
            iterations=settings.password_hash_iterations,
        )

    @provide(scope=Scope.APP)
    def provide_token_service(self, settings: IAMSettings) -> TokenService:
        return JWTTokenService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.access_token_expire_minutes,
            refresh_token_expire_minutes=settings.refresh_token_expire_minutes,
            verification_token_expire_minutes=settings.verification_token_expire_minutes,
            password_reset_token_expire_minutes=settings.password_reset_token_expire_minutes,
        )

    @provide(scope=Scope.APP)
    def provide_email_service(self, settings: IAMSettings) -> EmailService:
        return SMTPEmailService(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_username=settings.smtp_username,
            smtp_password=settings.smtp_password,
            from_email=settings.smtp_from_email,
            from_name=settings.smtp_from_name,
            use_tls=settings.smtp_use_tls,
            verification_url_template=settings.email_verification_url_template,
            password_reset_url_template=settings.email_password_reset_url_template,
            dashboard_url=settings.email_dashboard_url,
            support_email=settings.email_support_email,
        )

    @provide(scope=Scope.APP)
    def provide_user_token_service(self, token_service: TokenService) -> UserTokenService:
        return UserTokenService(token_service)

    @provide(scope=Scope.APP)
    def provide_user_repository(self) -> UserRepository:
        # TODO: Replace with real repository implementation
        # For production, use: SQLAlchemyUserRepository or similar
        return InMemoryUserRepository()

    @provide(scope=Scope.REQUEST)
    def provide_login_story(
        self,
        user_repo: UserRepository,
        hasher_service: HasherService,
        user_token_service: UserTokenService,
    ) -> Login:
        return Login(user_repo, hasher_service, user_token_service)

    @provide(scope=Scope.REQUEST)
    def provide_registration_story(
        self,
        user_repo: UserRepository,
        hasher_service: HasherService,
        user_token_service: UserTokenService,
        email_service: EmailService,
    ) -> Registeration:
        return Registeration(
            user_repo,
            hasher_service,
            user_token_service,
            email_service,
        )
