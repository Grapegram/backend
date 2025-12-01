from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.chat.application.contracts.repositories import ChatReadRepository
from src.core.chat.application.contracts.repositories.chat_read_repository import (
    ChatDTO,
    MessageDTO,
)
from src.core.chat.infrastructure.models import MessageModel
from src.core.chat.infrastructure.models.chat import ChatModel, MemberModel


class SQLAlchemyChatReadRepository(ChatReadRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_messages_by_chat_id(
        self, chat_id: str, limit: int, offset: int
    ) -> list[MessageDTO]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.chat_id == chat_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            MessageDTO(
                id=str(model.id),
                chat_id=str(model.chat_id),
                sender_id=model.sender_id,
                text=model.text,
                is_deleted=model.is_deleted,
                deleted_at=model.deleted_at,
                edited_at=model.edited_at,
                reactions=model.reactions if model.reactions else {},
                read_by=model.read_by if model.read_by else [],
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]

    async def count_messages_by_chat_id(self, chat_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(MessageModel)
            .where(MessageModel.chat_id == chat_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_chats_by_member_user_id(self, user_id: str) -> list[ChatDTO]:
        stmt = (
            select(ChatModel)
            .join(MemberModel, ChatModel.id == MemberModel.chat_id)
            .where(MemberModel.user_id == user_id)
            .order_by(ChatModel.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            ChatDTO(
                id=str(model.id),
                title=model.title,
                avatar=model.avatar,
                is_archived=model.is_archived,
                archived_at=model.archived_at,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]
