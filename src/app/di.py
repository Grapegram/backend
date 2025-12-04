from collections.abc import AsyncGenerator

from dishka import (
    AsyncContainer,
    Provider,
    Scope,
    from_context,
    make_async_container,
    provide,
)
from faststream.kafka import KafkaBroker
from litestar.channels import ChannelsPlugin
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.application.event_bus import EventBus
from seedwork.application.notifier import Notifier
from seedwork.application.object_storage import ObjectStorage
from seedwork.infrastructure.database import get_session
from seedwork.infrastructure.event_bus import FastStreamEventBus
from seedwork.infrastructure.notifier import LitestarNotifier
from seedwork.infrastructure.storage import AzureBlobStorage, S3ObjectStorage
from src.app.settings import Settings, StorageType, get_settings
from src.core.chat.infrastructure.di.providers import ChatProvider
from src.generic.iam.infrastructure.di import IAMProvider
from src.generic.iam.infrastructure.settings import IAMSettings


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_app_settings(self) -> Settings:
        return get_settings()

    @provide(scope=Scope.APP)
    async def provide_redis(self, settings: Settings) -> Redis:
        redis = Redis.from_url(str(settings.redis.url), decode_responses=False)
        return redis

    @provide(scope=Scope.APP)
    def provide_kafka_broker(self, settings: Settings) -> KafkaBroker:
        return KafkaBroker(f"{settings.kafka.host}:{settings.kafka.port}")

    @provide(scope=Scope.APP)
    def provide_event_bus(self, kafka_broker: KafkaBroker) -> EventBus:
        return FastStreamEventBus(kafka_broker)

    @provide(scope=Scope.APP)
    def provide_object_storage(self, settings: Settings) -> ObjectStorage:
        if settings.storage_type == StorageType.S3:
            return S3ObjectStorage(
                endpoint_url=settings.s3.endpoint_url,
                access_key_id=settings.s3.access_key_id,
                secret_access_key=settings.s3.secret_access_key,
                region_name=settings.s3.region_name,
                public_url=settings.s3.public_url,
                use_ssl=settings.s3.use_ssl,
                default_bucket=settings.s3.bucket_name,
            )
        elif settings.storage_type == StorageType.AZURE:
            return AzureBlobStorage(
                connection_string=settings.azure.connection_string,
                account_name=settings.azure.account_name,
                account_key=settings.azure.account_key,
                container_name=settings.azure.container_name,
                public_url=settings.azure.public_url,
                default_bucket=settings.azure.bucket_name,
            )
        else:
            raise ValueError(f"Unsupported storage type: {settings.storage_type}")

    @provide(scope=Scope.REQUEST)
    async def provide_session(self, settings: Settings) -> AsyncGenerator[AsyncSession]:
        async for session in get_session(settings.postgres.url, False):
            yield session

    channels_plugin = from_context(provides=ChannelsPlugin, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    def provide_notifier(self, channels: ChannelsPlugin) -> Notifier:
        return LitestarNotifier(channels)

    @provide(scope=Scope.APP)
    def provide_iam_settings(self, settings: Settings) -> IAMSettings:
        return IAMSettings(
            jwt_secret_key=settings.jwt.secret_key,
            jwt_algorithm=settings.jwt.algorithm,
            access_token_expire_minutes=settings.jwt.access_token_expire_minutes,
            refresh_token_expire_minutes=settings.jwt.refresh_token_expire_minutes,
            verification_token_expire_minutes=settings.jwt.verification_token_expire_minutes,
            password_reset_token_expire_minutes=settings.jwt.password_reset_token_expire_minutes,
            password_salt=settings.hash.salt,
            password_hash_iterations=settings.hash.hash_iterations,
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


def create_container(channels_plugin: ChannelsPlugin) -> AsyncContainer:
    return make_async_container(
        SettingsProvider(),
        IAMProvider(),
        ChatProvider(),
        context={
            ChannelsPlugin: channels_plugin,
        },
    )
