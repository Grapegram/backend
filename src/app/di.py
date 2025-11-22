from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from faststream.redis.annotations import RedisBroker

from seedwork.application.event_bus import EventBus
from seedwork.infrastructure.event_bus import FastStreamEventBus
from src.app.settings import Settings, get_settings
from src.generic.iam.infrastructure.di import IAMProvider
from src.generic.iam.infrastructure.settings import IAMSettings


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_app_settings(self) -> Settings:
        return get_settings()

    @provide(scope=Scope.APP)
    def provide_event_bus(self, settings: Settings) -> RedisBroker:
        print(settings.redis.url)
        return RedisBroker(settings.redis.url)

    @provide(scope=Scope.APP)
    def provide_redis_bus(self, redis_bus: RedisBroker) -> EventBus:
        return FastStreamEventBus(redis_bus)

    @provide(scope=Scope.APP)
    def provide_iam_settings(self, settings: Settings) -> IAMSettings:
        return IAMSettings(
            jwt_secret_key=settings.jwt.secret_key,
            jwt_algorithm=settings.jwt.algorithm,
            access_token_expire_minutes=settings.jwt.access_token_expire_minutes,
            refresh_token_expire_minutes=settings.jwt.refresh_token_expire_minutes,
            verification_token_expire_minutes=settings.jwt.verification_token_expire_minutes,
            password_reset_token_expire_minutes=settings.jwt.password_reset_token_expire_minutes,
            smtp_host=settings.smtp.host,
            smtp_port=settings.smtp.port,
            smtp_username=settings.smtp.username,
            smtp_password=settings.smtp.password,
            smtp_from_email=settings.smtp.from_email,
            smtp_from_name=settings.smtp.from_name,
            smtp_use_tls=settings.smtp.use_tls,
            email_verification_url_template=settings.smtp.verification_url_template,
            email_password_reset_url_template=settings.smtp.password_reset_url_template,
            email_dashboard_url=settings.smtp.dashboard_url,
            email_support_email=settings.smtp.support_email,
        )


def create_container() -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        IAMProvider(),
    )
