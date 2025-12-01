from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.domain.repositories.exceptions import EntityNotFoundException
from seedwork.domain.services.clock import utcnow
from src.generic.iam.domain.aggregates import User
from src.generic.iam.domain.mappers import to_user
from src.generic.iam.domain.repositories import UserRepository
from src.generic.iam.domain.value_objects import UserId
from src.generic.iam.infrastructure.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def to_persistence(self, entity: User) -> UserModel:
        now = utcnow()
        return UserModel(
            id=entity.id,
            email=str(entity.email),
            username=entity.username,
            hashed_password=str(entity.hashed_password),
            avatar=entity.avatar,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            last_login_at=entity.last_login_at,
            created_at=now,
            updated_at=now,
        )

    def update_model(self, entity: User, model: UserModel) -> None:
        model.email = str(entity.email)
        model.username = entity.username
        model.hashed_password = str(entity.hashed_password)
        model.avatar = entity.avatar
        model.is_active = entity.is_active
        model.is_verified = entity.is_verified
        model.last_login_at = entity.last_login_at
        model.updated_at = utcnow()

    async def save(self, entity: User) -> None:
        stmt = select(UserModel).where(UserModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model is None:
            model = self.to_persistence(entity)
            self._session.add(model)
        else:
            self.update_model(entity, existing_model)

        await self._session.flush()

    async def get(self, entity_id: UserId) -> Maybe[User]:
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_user(model))

    async def delete(self, entity_id: UserId) -> Result[None, EntityNotFoundException]:
        stmt = select(UserModel).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Failure(
                EntityNotFoundException(
                    entity_id=entity_id,
                    entity_type="User",
                )
            )

        await self._session.delete(model)
        await self._session.flush()

        return Success(None)

    async def exists(self, entity_id: UserId) -> bool:
        stmt = select(UserModel.id).where(UserModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_email(self, email: str) -> Maybe[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_user(model))

    async def get_by_username(self, username: str) -> Maybe[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_user(model))

    async def all(self) -> list[User]:
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_user(model) for model in models]

    async def count(self) -> int:
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
