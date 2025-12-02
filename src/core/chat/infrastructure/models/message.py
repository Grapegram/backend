from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from seedwork.infrastructure.database import Base


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    chat_id: Mapped[UUID] = mapped_column(String(255), nullable=False, index=True)
    sender_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reactions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    read_by: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
