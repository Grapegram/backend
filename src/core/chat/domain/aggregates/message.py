"""
Message Aggregate Root

Represents a message in a chat conversation.
A message is an independent aggregate that belongs to a chat.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from returns.result import Result, Success

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.services.clock import utcnow
from seedwork.returns import catch_unwrap
from src.core.chat.domain.value_objects.member_id import MemberId

from ..entities import Member
from ..events import (
    MessageDeleted,
    MessageEdited,
    MessageReactionAdded,
    MessageReactionRemoved,
    MessageRead,
    MessageSent,
)
from ..rules.message import (
    MessageCannotBeEditedAfterDeletion,
    MessageCannotHaveMoreThanMaxImages,
    MessageMustBelongToChat,
    MessageMustHaveTextOrImages,
    NewMessageTextMustBeDifferent,
    OnlyAuthorCanEditMessage,
    OnlyAuthorOrAdminCanDeleteMessage,
)
from ..value_objects import ChatId, MessageId, MessageText, Reaction


@dataclass
class Message(AggregateRoot[MessageId]):
    """
    Message aggregate root representing a message in a chat.

    This is an aggregate root that manages message content,
    reactions, and ensures business rules are enforced.
    """

    id: MessageId
    chat_id: ChatId
    sender_id: MemberId
    sent_at: datetime
    text: MessageText | None
    images: list[str] = field(default_factory=list)
    is_deleted: bool = False
    deleted_at: datetime | None = None
    edited_at: datetime | None = None
    reactions: dict[MemberId, list[Reaction]] = field(default_factory=dict)
    read_by: list[MemberId] = field(default_factory=list)

    @classmethod
    @catch_unwrap
    def create(
        cls,
        chat_id: str,
        sender_id: str,
        text: str | None = None,
        images: list[str] | None = None,
    ) -> Result[
        Self,
        VOValidationException
        | MessageCannotHaveMoreThanMaxImages
        | MessageMustHaveTextOrImages,
    ]:
        message_id = MessageId.next_id()
        chat_id_vo = ChatId(chat_id)
        text_vo = MessageText(text).unwrap() if text else None
        images = images or []
        now = utcnow()

        message = cls(
            id=message_id,
            chat_id=chat_id_vo,
            sender_id=sender_id,
            text=text_vo,
            images=images,
            sent_at=now,
        )

        message.check_rule(
            MessageCannotHaveMoreThanMaxImages(images_count=len(images))
        ).unwrap()
        message.check_rule(
            MessageMustHaveTextOrImages(has_text=bool(text_vo), has_images=bool(images))
        ).unwrap()

        message.register_event(
            MessageSent(
                message_id=message_id,
                chat_id=chat_id_vo,
                sender_id=sender_id,
                text=str(text_vo) if text_vo else "",
                images=images,
                sent_at=now,
            )
        )

        return Success(message)

    @catch_unwrap
    def edit_text(
        self, new_text: str, editor_id: str
    ) -> Result[None, VOValidationException]:
        self.check_rule(
            OnlyAuthorCanEditMessage(author_id=self.sender_id, editor_id=editor_id)
        ).unwrap()
        self.check_rule(
            MessageCannotBeEditedAfterDeletion(is_deleted=self.is_deleted)
        ).unwrap()

        text_vo = MessageText(new_text).unwrap()

        # Only check if text is different if current text exists
        if self.text:
            self.check_rule(
                NewMessageTextMustBeDifferent(current_text=self.text, new_text=text_vo)
            ).unwrap()

        old_text = str(self.text) if self.text else ""
        self.text = text_vo
        self.edited_at = utcnow()

        self.register_event(
            MessageEdited(
                message_id=self.id,
                chat_id=self.chat_id,
                old_text=old_text,
                new_text=str(text_vo),
                edited_by=editor_id,
                edited_at=self.edited_at,
            )
        )

    @catch_unwrap
    def delete(self, deleter: Member) -> Result[None, VOValidationException]:
        if self.is_deleted:
            return  # Already deleted

        self.check_rule(
            MessageMustBelongToChat(
                message_chat_id=str(self.chat_id),
                expected_chat_id=deleter.chat_id,
            )
        ).unwrap()

        self.check_rule(
            OnlyAuthorOrAdminCanDeleteMessage(author_id=self.sender_id, deleter=deleter)
        ).unwrap()

        self.is_deleted = True
        self.deleted_at = utcnow()

        self.register_event(
            MessageDeleted(
                message_id=self.id,
                chat_id=self.chat_id,
                deleted_by=deleter.user_id,
                deleted_at=self.deleted_at,
            )
        )

    def add_reaction(self, user_id: str, reaction: str) -> None:
        if self.is_deleted:
            raise ValueError("Cannot add reaction to a deleted message")

        if reaction not in self.reactions:
            self.reactions[reaction] = []

        if user_id not in self.reactions[reaction]:
            self.reactions[reaction].append(user_id)

            self.register_event(
                MessageReactionAdded(
                    message_id=self.id,
                    chat_id=self.chat_id,
                    user_id=user_id,
                    reaction=reaction,
                    added_at=self.updated_at,
                )
            )

    def remove_reaction(self, user_id: str, reaction: str) -> None:
        if reaction not in self.reactions:
            return

        if user_id in self.reactions[reaction]:
            self.reactions[reaction].remove(user_id)

            # Clean up empty reaction lists
            if not self.reactions[reaction]:
                del self.reactions[reaction]

            self.register_event(
                MessageReactionRemoved(
                    message_id=self.id,
                    chat_id=self.chat_id,
                    user_id=user_id,
                    reaction=reaction,
                    removed_at=self.updated_at,
                )
            )

    def mark_as_read(self, user_id: str) -> None:
        """
        Mark the message as read by a user.

        Args:
            user_id: The user ID who reads the message
        """
        if user_id not in self.read_by:
            self.read_by.append(user_id)

            self.register_event(
                MessageRead(
                    message_id=self.id,
                    chat_id=self.chat_id,
                    user_id=user_id,
                    read_at=self.updated_at,
                )
            )

    def get_reaction_count(self, reaction: str) -> int:
        """Get the count of a specific reaction."""
        return len(self.reactions.get(reaction, []))

    def get_total_reactions(self) -> int:
        """Get the total number of reactions."""
        return sum(len(users) for users in self.reactions.values())

    def has_user_reacted(self, user_id: str, reaction: str) -> bool:
        """Check if a user has reacted with a specific emoji."""
        return user_id in self.reactions.get(reaction, [])

    def is_read_by(self, user_id: str) -> bool:
        """Check if the message is read by a specific user."""
        return user_id in self.read_by

    def is_edited(self) -> bool:
        """Check if the message has been edited."""
        return self.edited_at is not None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, Message):
            return self.id == other.id
        return False
