from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.domain.repositories.exceptions import EntityNotFoundException
from seedwork.domain.services.clock import utcnow
from src.core.chat.domain.aggregates import Message
from src.core.chat.domain.mappers import to_message
from src.core.chat.domain.repositories import MessageRepository
from src.core.chat.domain.value_objects import MessageId
from src.core.chat.infrastructure.mappers.message import message_to_model
from src.core.chat.infrastructure.models import MessageModel


class SQLAlchemyMessageRepository(MessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def to_persistence(self, entity: Message) -> MessageModel:
        return message_to_model(entity)

    def update_model(self, entity: Message, model: MessageModel) -> None:
        model.text = str(entity.text)
        model.is_deleted = entity.is_deleted
        model.deleted_at = entity.deleted_at
        model.edited_at = entity.edited_at
        model.reactions = entity.reactions if entity.reactions else {}
        model.read_by = entity.read_by if entity.read_by else []
        model.updated_at = utcnow()

    async def save(self, entity: Message) -> None:
        stmt = select(MessageModel).where(MessageModel.id == entity.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        if existing_model is None:
            model = self.to_persistence(entity)
            self._session.add(model)
        else:
            self.update_model(entity, existing_model)

        await self._session.flush()

    async def get(self, entity_id: MessageId) -> Maybe[Message]:
        stmt = select(MessageModel).where(MessageModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Nothing

        return Some(to_message(model))

    async def delete(
        self, entity_id: MessageId
    ) -> Result[None, EntityNotFoundException]:
        stmt = select(MessageModel).where(MessageModel.id == entity_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return Failure(
                EntityNotFoundException(
                    entity_id=entity_id,
                    entity_type="Message",
                )
            )

        await self._session.delete(model)
        await self._session.flush()

        return Success(None)

    async def exists(self, entity_id: MessageId) -> bool:
        stmt = select(MessageModel.id).where(MessageModel.id == entity_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_chat_id(
        self, chat_id: str, limit: int = 50, offset: int = 0
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_message(model) for model in models]

    async def get_by_sender_id(self, sender_id: str) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.sender_id == sender_id)
            .order_by(MessageModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_message(model) for model in models]

    async def count_by_chat_id(self, chat_id: str) -> int:
        stmt = select(MessageModel).where(MessageModel.chat_id == chat_id)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    async def all(self) -> list[Message]:
        stmt = select(MessageModel).order_by(MessageModel.created_at.desc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [to_message(model) for model in models]

    async def count(self) -> int:
        stmt = select(MessageModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
