from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.app.settings import get_settings


class DatabaseSessionFactory:
    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    def create_session(self) -> AsyncSession:
        return self._session_factory()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        await self._engine.dispose()


_session_factory: DatabaseSessionFactory | None = None


def get_session_factory() -> DatabaseSessionFactory:
    global _session_factory
    if _session_factory is None:
        settings = get_settings()
        engine = create_async_engine(
            settings.postgres.url,
            echo=settings.core.debug,
            pool_pre_ping=True,
        )
        _session_factory = DatabaseSessionFactory(engine)
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    factory = get_session_factory()
    async with factory.session() as session:
        yield session


class Base(DeclarativeBase): ...
