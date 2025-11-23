from functools import lru_cache
from pathlib import Path
from typing import Any, Unpack

from envparse import Env
from pydantic import (
    BaseModel,
    Field,
    PostgresDsn,
    RedisDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_FOLDER = Path(__file__).parent.parent.parent
CERTS_FOLDER = PROJECT_FOLDER / "certs"
_sentinel: Any = object()


def get_model_config(**kwargs: Unpack[SettingsConfigDict]) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        **kwargs,
    )


class CoreSettings(BaseSettings):
    project_folder: Path = PROJECT_FOLDER
    project_name: str
    debug: bool = True
    secret: str
    host: str
    port: int
    api_version: int
    api_prefix: str = Field("/api/v{version}", validate_default=True)

    @field_validator("api_prefix", mode="before")
    @classmethod
    def assemble_api_prefix(cls, v: str, values: ValidationInfo) -> str:
        return v.format(version=values.data.get("api_version"))


class RedisSettings(BaseModel):
    driver: str = "redis"
    host: str
    port: int
    user: str | None = None
    password: str | None = None
    url: str = Field(_sentinel, validate_default=True)

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: str | RedisDsn, values: ValidationInfo
    ) -> RedisDsn:
        if isinstance(v, str):
            return RedisDsn(v)

        return str(
            RedisDsn.build(
                scheme=values.data.get("driver"),
                username=values.data.get("user"),
                password=values.data.get("password"),
                host=values.data.get("host"),
                port=values.data.get("port"),
            )
        )


class PostgresSettings(BaseModel):
    driver: str
    host: str
    port: int
    user: str
    password: str
    db: str
    url: str = Field(_sentinel, validate_default=True)

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: str | PostgresDsn, values: ValidationInfo
    ) -> PostgresDsn:
        if isinstance(v, str):
            return str(PostgresDsn(v))

        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{values.data.get('driver')}",
                username=values.data.get("user"),
                password=values.data.get("password"),
                host=values.data.get("host"),
                port=values.data.get("port"),
                path=f"{values.data.get('db') or ''}",
            )
        )


class JWTSettings(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    verification_token_expire_minutes: int = 60 * 24  # 24 hours
    password_reset_token_expire_minutes: int = 60  # 1 hour


class HashSettings(BaseModel):
    secret_key: str
    hash_iterations: int = 600_000

    @property
    def salt(self) -> bytes:
        return self.secret_key.encode("utf-8")


class SMTPSettings(BaseModel):
    host: str = "mailpit"
    port: int = 1025
    username: str = ""
    password: str = ""
    from_email: str = "noreply@grapegram.com"
    from_name: str = "Grapegram"
    use_tls: bool = False

    # Email URL Templates
    verification_url_template: str = "https://grapegram.com/verify-email?token={token}"
    password_reset_url_template: str = (
        "https://grapegram.com/reset-password?token={token}"
    )
    dashboard_url: str = "https://grapegram.com/dashboard"
    support_email: str = "support@grapegram.com"


class Settings(BaseSettings):
    core: CoreSettings = Field(default_factory=CoreSettings)
    jwt: JWTSettings
    hash: HashSettings
    smtp: SMTPSettings
    postgres: PostgresSettings
    redis: RedisSettings

    model_config = get_model_config()


@lru_cache
def get_settings() -> Settings:
    env = Env()
    env.read_envfile(PROJECT_FOLDER / "env" / ".env")

    return Settings()
