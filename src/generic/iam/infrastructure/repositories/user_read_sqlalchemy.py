from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.application.object_storage import ObjectStorage
from src.generic.iam.application.contracts.repositories import (
    UserDTO,
    UserListFilters,
    UserReadRepository,
)
from src.generic.iam.infrastructure.models import UserModel


class SQLAlchemyUserReadRepository(UserReadRepository):
    def __init__(self, session: AsyncSession, object_storage: ObjectStorage):
        self._session = session
        self._object_storage = object_storage

    async def get_users_list(self, filters: UserListFilters) -> list[UserDTO]:
        stmt = select(UserModel)

        # Apply filters
        conditions = []

        if filters.search:
            search_pattern = f"%{filters.search}%"
            conditions.append(
                or_(
                    UserModel.username.ilike(search_pattern),
                    UserModel.email.ilike(search_pattern),
                )
            )

        if filters.is_active is not None:
            conditions.append(UserModel.is_active == filters.is_active)

        if filters.is_verified is not None:
            conditions.append(UserModel.is_verified == filters.is_verified)

        if conditions:
            stmt = stmt.where(*conditions)

        # Apply ordering
        stmt = stmt.order_by(UserModel.created_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            UserDTO(
                id=str(model.id),
                email=model.email,
                username=model.username,
                avatar=await self._resolve_avatar_url(model.avatar),
                is_active=model.is_active,
                is_verified=model.is_verified,
                last_login_at=model.last_login_at,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]

    async def get_user_by_id(self, user_id: str) -> UserDTO | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return UserDTO(
            id=str(model.id),
            email=model.email,
            username=model.username,
            avatar=await self._resolve_avatar_url(model.avatar),
            is_active=model.is_active,
            is_verified=model.is_verified,
            last_login_at=model.last_login_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def _resolve_avatar_url(self, avatar_key: str | None) -> str | None:
        if not avatar_key:
            return None
        return await self._object_storage.get_file_url(key=avatar_key)
