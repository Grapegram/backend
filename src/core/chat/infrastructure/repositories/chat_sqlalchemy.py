from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.domain.repositories.exceptions import EntityNotFoundException
from seedwork.domain.services.clock import utcnow
from src.core.chat.domain.aggregates import Chat
from src.core.chat.domain.mappers import to_chat
from src.core.chat.domain.repositories import ChatRepository
from src.core.chat.domain.value_objects import ChatId, ChatType
from src.core.chat.infrastructure.mappers.chat import chat_to_model, member_to_model
from src.core.chat.infrastructure.models import ChatModel, MemberModel


class SQLAlchemyChatRepository(ChatRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def to_persistence(self, entity: Chat) -> ChatModel:
        return chat_to_model(entity)

    def update_model(self, entity: Chat, model: ChatModel) -> None:
        model.title = str(entity.title)
        model.type = entity.type.value
        model.is_archived = entity.is_archived
        model.archived_at = entity.archived_at
        model.avatar = entity.avatar
        model.updated_at = utcnow()

        existing_member_ids = {member.id for member in model.members}
        entity_member_ids = {member.id for member in entity.members}

        members_to_delete = existing_member_ids - entity_member_ids
        for member_model in list(model.members):
            if member_model.id in members_to_delete:
                model.members.remove(member_model)

        members_to_add = entity_member_ids - existing_member_ids
        for member in entity.members:
            if member.id in members_to_add:
                member_model = member_to_model(member, entity.id)
                model.members.append(member_model)

        for member in entity.members:
            if member.id not in members_to_add:
                for member_model in model.members:
                    if member_model.id == member.id:
                        member_model.user_id = member.user_id
                        member_model.role = member.role.value
                        member_model.last_read_at = member.last_read_at
                        break

    async def save(self, entity: Chat) -> None:
        stmt = select(ChatModel).where(ChatModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model is None:
            model = self.to_persistence(entity)
            for member in entity.members:
                member_model = member_to_model(member, entity.id)
                model.members.append(member_model)
            self._session.add(model)
        else:
            self.update_model(entity, existing_model)

        await self._session.flush()

    async def get(self, entity_id: ChatId) -> Maybe[Chat]:
        stmt = select(ChatModel).where(ChatModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_chat(model))

    async def delete(self, entity_id: ChatId) -> Result[None, EntityNotFoundException]:
        stmt = select(ChatModel).where(ChatModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Failure(
                EntityNotFoundException(
                    entity_id=entity_id,
                    entity_type="Chat",
                )
            )

        await self._session.delete(model)
        await self._session.flush()

        return Success(None)

    async def exists(self, entity_id: ChatId) -> bool:
        stmt = select(ChatModel.id).where(ChatModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_user_id(self, user_id: str) -> list[Chat]:
        stmt = (
            select(ChatModel)
            .join(MemberModel)
            .where(MemberModel.user_id == user_id)
            .order_by(ChatModel.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_chat(model) for model in models]

    async def get_by_member_user_id(self, user_id: str) -> list[Chat]:
        return await self.get_by_user_id(user_id)

    async def get_direct_chat_between(
        self, user1_id: str, user2_id: str
    ) -> Maybe[Chat]:
        # Find direct chats where both users are members
        # Subquery to count members for each chat
        member_count_subquery = (
            select(
                MemberModel.chat_id, func.count(MemberModel.id).label("member_count")
            )
            .group_by(MemberModel.chat_id)
            .subquery()
        )

        # Find chats where user1 is a member
        user1_chats = (
            select(MemberModel.chat_id)
            .where(MemberModel.user_id == user1_id)
            .subquery()
        )

        # Find chats where user2 is a member
        user2_chats = (
            select(MemberModel.chat_id)
            .where(MemberModel.user_id == user2_id)
            .subquery()
        )

        # Find direct chats with exactly 2 members where both users are members
        stmt = (
            select(ChatModel)
            .join(
                member_count_subquery, ChatModel.id == member_count_subquery.c.chat_id
            )
            .where(
                and_(
                    ChatModel.type == ChatType.DIRECT.value,
                    member_count_subquery.c.member_count == 2,
                    ChatModel.id.in_(user1_chats),
                    ChatModel.id.in_(user2_chats),
                )
            )
            .limit(1)
        )

        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_chat(model))

    async def all(self) -> list[Chat]:
        stmt = select(ChatModel).order_by(ChatModel.created_at.desc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_chat(model) for model in models]

    async def count(self) -> int:
        stmt = select(ChatModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
