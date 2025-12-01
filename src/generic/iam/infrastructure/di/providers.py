from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.application.event_bus import EventBus
from seedwork.application.object_storage import ObjectStorage
from src.generic.iam.application.contracts.email import EmailService
from src.generic.iam.application.contracts.hasher import HasherService
from src.generic.iam.application.contracts.repositories import UserReadRepository
from src.generic.iam.application.contracts.token import TokenService
from src.generic.iam.application.handlers.queries import (
    GetCurrentUser,
    GetUsersList,
)
from src.generic.iam.application.handlers.send_verification_email import (
    SendVerificationEmail,
)
from src.generic.iam.application.services.auth import AuthService
from src.generic.iam.application.services.user import UserService
from src.generic.iam.application.services.user_token import UserTokenService
from src.generic.iam.application.use_cases.change_user_avatar import ChangeUserAvatar
from src.generic.iam.application.use_cases.login import Login
from src.generic.iam.application.use_cases.registration_by_email import (
    RegistrationByEmail,
)
from src.generic.iam.application.use_cases.verification_email import VerifyEmail
from src.generic.iam.domain.repositories import UserRepository
from src.generic.iam.infrastructure.repositories import (
    SQLAlchemyUserReadRepository,
    SQLAlchemyUserRepository,
)
from src.generic.iam.infrastructure.services import (
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

    @provide(scope=Scope.REQUEST)
    def provide_auth(
        self, user_repository: UserRepository, token_service: UserTokenService
    ) -> AuthService:
        return AuthService(user_repository=user_repository, token_service=token_service)

    @provide(scope=Scope.APP)
    def provide_user_token_service(
        self, token_service: TokenService
    ) -> UserTokenService:
        return UserTokenService(token_service)

    @provide(scope=Scope.APP)
    def provide_user_service(self, object_sotrage: ObjectStorage) -> UserService:
        return UserService(object_storage=object_sotrage)

    @provide(scope=Scope.REQUEST)
    def provide_user_repository(self, session: AsyncSession) -> UserRepository:
        return SQLAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_user_read_repository(
        self, session: AsyncSession, object_storage: ObjectStorage
    ) -> UserReadRepository:
        return SQLAlchemyUserReadRepository(session, object_storage)

    @provide(scope=Scope.REQUEST)
    def provide_get_current_user_handler(
        self,
        user_read_repo: UserReadRepository,
    ) -> GetCurrentUser:
        return GetCurrentUser(user_read_repo=user_read_repo)

    @provide(scope=Scope.REQUEST)
    def provide_get_users_list_handler(
        self,
        user_read_repo: UserReadRepository,
    ) -> GetUsersList:
        return GetUsersList(user_read_repo=user_read_repo)

    @provide(scope=Scope.REQUEST)
    def provide_send_verification_email(
        self,
        user_token_service: UserTokenService,
        email_service: EmailService,
    ) -> SendVerificationEmail:
        return SendVerificationEmail(
            user_token_service=user_token_service,
            email_service=email_service,
        )

    @provide(scope=Scope.REQUEST)
    def provide_login_story(
        self,
        user_repo: UserRepository,
        hasher_service: HasherService,
        user_token_service: UserTokenService,
    ) -> Login:
        return Login(
            user_repo=user_repo,
            hasher_service=hasher_service,
            user_token_service=user_token_service,
        )

    @provide(scope=Scope.REQUEST)
    def provide_registration_story(
        self,
        event_bus: EventBus,
        user_repo: UserRepository,
        hasher_service: HasherService,
        user_token_service: UserTokenService,
    ) -> RegistrationByEmail:
        return RegistrationByEmail(
            event_bus=event_bus,
            user_repo=user_repo,
            hasher_service=hasher_service,
            user_token_service=user_token_service,
        )

    @provide(scope=Scope.REQUEST)
    def provide_verify_email_story(
        self,
        user_token_service: UserTokenService,
        user_repo: UserRepository,
    ) -> VerifyEmail:
        return VerifyEmail(
            user_token_service=user_token_service,
            user_repo=user_repo,
        )

    @provide(scope=Scope.REQUEST)
    def provide_change_user_avatar_story(
        self,
        user_repo: UserRepository,
        user_service: UserService,
        event_bus: EventBus,
    ) -> ChangeUserAvatar:
        return ChangeUserAvatar(
            user_repo=user_repo,
            user_service=user_service,
            event_bus=event_bus,
        )
