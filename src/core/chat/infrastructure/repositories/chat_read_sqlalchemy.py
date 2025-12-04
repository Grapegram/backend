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
from src.core.chat.application.contracts.user_status import UserStatusService
from src.core.chat.infrastructure.models import MessageModel
from src.core.chat.infrastructure.models.chat import ChatModel, MemberModel


class SQLAlchemyChatReadRepository(ChatReadRepository):
    def __init__(
        self,
        session: AsyncSession,
        object_storage: ObjectStorage,
        user_status_service: UserStatusService,
    ):
        self._session = session
        self._object_storage = object_storage
        self._user_status_service = user_status_service

    async def get_messages_by_chat_id(
        self, chat_id: str, from_message_id: str | None, limit: int
    ) -> list[MessageDTO]:
        stmt = select(MessageModel).where(MessageModel.chat_id == chat_id)

        if from_message_id:
            # Get the created_at timestamp of the reference message
            ref_stmt = select(MessageModel.created_at).where(
                MessageModel.id == from_message_id
            )
            ref_result = await self._session.execute(ref_stmt)
            ref_created_at = ref_result.scalar_one_or_none()

            if ref_created_at:
                # Fetch messages created before the reference message
                stmt = stmt.where(MessageModel.created_at < ref_created_at)

        stmt = stmt.order_by(MessageModel.created_at.desc()).limit(limit)

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

        chats = []
        for model in models:
            typing_users = await self._user_status_service.get_typing_users(
                str(model.id)
            )
            chats.append(
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
                            is_typing=member.user_id in typing_users,
                            joined_at=member.joined_at,
                        )
                        for member in model.members
                    ],
                )
            )
        return chats

    async def get_chat_by_id(self, chat_id: str) -> ChatDTO | None:
        stmt = (
            select(ChatModel)
            .where(ChatModel.id == chat_id)
            .options(selectinload(ChatModel.members))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        typing_users = await self._user_status_service.get_typing_users(chat_id)

        return ChatDTO(
            id=str(model.id),
            title=model.title,
            type=model.type,
            avatar=await self._resolve_avatar_url(model.avatar),
            members=[
                ChatMemberDTO(
                    id=str(member.id),
                    user_id=member.user_id,
                    role=member.role,
                    is_typing=member.user_id in typing_users,
                    joined_at=member.joined_at,
                )
                for member in model.members
            ],
        )

    async def _resolve_avatar_url(self, avatar_key: str | None) -> str | None:
        if not avatar_key:
            return None
        return await self._object_storage.get_file_url(key=avatar_key)
