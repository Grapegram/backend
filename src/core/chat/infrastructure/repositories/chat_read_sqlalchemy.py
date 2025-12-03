from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from seedwork.application.object_storage import ObjectStorage
from src.core.chat.application.contracts.repositories import ChatReadRepository
from src.core.chat.application.contracts.repositories.chat_read_repository import (
    ChatDTO,
    ChatMemberDTO,
    MessageDTO,
)
from src.core.chat.infrastructure.models import MessageModel
from src.core.chat.infrastructure.models.chat import ChatModel, MemberModel


class SQLAlchemyChatReadRepository(ChatReadRepository):
    def __init__(self, session: AsyncSession, object_storage: ObjectStorage):
        self._session = session
        self._object_storage = object_storage

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
                text=model.text or None,
                images=await self.fetch_images(model.images or []),
                sent_at=model.created_at,
                edited_at=model.edited_at,
                reactions=model.reactions if model.reactions else {},
                read_by=model.read_by if model.read_by else [],
            )
            for model in models
        ]

    async def fetch_images(self, imgs: list[str]):
        return [await self._object_storage.get_file_url(key=img) for img in imgs]

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
            .options(selectinload(ChatModel.members))
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            ChatDTO(
                id=str(model.id),
                title=model.title,
                type=model.type,
                avatar=await self._resolve_avatar_url(model.avatar),
                members=[
                    ChatMemberDTO(
                        id=str(member.id),
                        user_id=member.user_id,
                        role=member.role,
                        joined_at=member.joined_at,
                    )
                    for member in model.members
                ],
            )
            for model in models
        ]

    async def _resolve_avatar_url(self, avatar_key: str | None) -> str | None:
        if not avatar_key:
            return None
        return await self._object_storage.get_file_url(key=avatar_key)
