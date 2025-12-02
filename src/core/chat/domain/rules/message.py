"""
Message Business Rules

Business rules that govern the Message aggregate behavior.
"""

from dataclasses import dataclass

from seedwork.domain.rule import BusinessRule

from ..entities import Member
from ..value_objects import MessageText


@dataclass
class OnlyAuthorCanEditMessage(BusinessRule):
    """Only the message author can edit their own message."""

    author_id: str
    editor_id: str

    def is_broken(self) -> bool:
        return self.author_id != self.editor_id


@dataclass
class OnlyAuthorOrAdminCanDeleteMessage(BusinessRule):
    """Only the message author or an admin can delete the message."""

    author_id: str
    deleter: Member

    def is_broken(self) -> bool:
        # Admin can delete any message
        if self.deleter.has_admin_privileges():
            return False
        # Author can delete their own message
        return self.author_id != self.deleter.user_id


@dataclass
class MemberCannotSendMessageIfMuted(BusinessRule):
    """You are muted and cannot send messages in this chat."""

    sender: Member

    def is_broken(self) -> bool:
        return not self.sender.can_send_messages()


@dataclass
class MessageCannotBeEditedAfterDeletion(BusinessRule):
    """Cannot edit a deleted message."""

    is_deleted: bool

    def is_broken(self) -> bool:
        return self.is_deleted


@dataclass
class NewMessageTextMustBeDifferent(BusinessRule):
    """The new message text must be different from the current text."""

    current_text: MessageText
    new_text: MessageText

    def is_broken(self) -> bool:
        return self.current_text == self.new_text


@dataclass
class MessageMustBelongToChat(BusinessRule):
    """The message does not belong to this chat."""

    message_chat_id: str
    expected_chat_id: str

    def is_broken(self) -> bool:
        return self.message_chat_id != self.expected_chat_id


@dataclass
class MessageCannotHaveMoreThanMaxImages(BusinessRule):
    """A message cannot have more than 10 images."""

    images_count: int
    max_images: int = 10

    def is_broken(self) -> bool:
        return self.images_count > self.max_images


@dataclass
class MessageMustHaveTextOrImages(BusinessRule):
    """A message must have either text or at least one image."""

    has_text: bool
    has_images: bool

    def is_broken(self) -> bool:
        return not self.has_text and not self.has_images
