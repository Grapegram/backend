from functools import lru_cache
from pathlib import Path
from typing import Any, Unpack

from envparse import Env
from pydantic import (
    Field,
    PostgresDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_FOLDER = Path(__file__).parent.parent.parent
_sentinel: Any = object()


def get_model_config(**kwargs: Unpack[SettingsConfigDict]) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        **kwargs,
    )


class PostgresSettings(BaseSettings):
    driver: str
    host: str
    port: int
    user: str
    password: str
    db: str
    url: PostgresDsn = Field(_sentinel, validate_default=True)

    model_config = get_model_config(env_prefix="POSTGRES_")

    @field_validator("url", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: str | PostgresDsn, values: ValidationInfo
    ) -> PostgresDsn:
        if isinstance(v, str):
            return PostgresDsn(v)

        return PostgresDsn.build(
            scheme=f"postgresql+{values.data.get('driver')}",
            username=values.data.get("user"),
            password=values.data.get("password"),
            host=f"{values.data.get('host')}:{values.data.get('port')}",
            path=f"{values.data.get('db') or ''}",
        )


class CoreSettings(BaseSettings):
    project_folder: Path = PROJECT_FOLDER
    project_name: str
    secret_key: str
    debug: bool = False
    host: str
    port: int
    api_version: int
    api_prefix: str = Field("/api/v{version}", validate_default=True)

    @field_validator("api_prefix", mode="before")
    @classmethod
    def assemble_api_prefix(cls, v: str, values: ValidationInfo) -> str:
        return v.format(version=values.data.get("api_version"))


class Settings(BaseSettings):
    core: CoreSettings = Field(default_factory=CoreSettings)
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)

    model_config = get_model_config()


@lru_cache
def get_settings() -> Settings:
    env = Env()
    env.read_envfile(PROJECT_FOLDER / "env" / ".env")

    return Settings()
