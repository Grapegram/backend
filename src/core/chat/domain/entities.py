from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Self

from returns.result import Result, Success

from seedwork.domain.entities import Entity
from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.services.clock import utcnow
from seedwork.returns import catch_unwrap

from .value_objects import MemberId


class MemberRole(Enum):
    """Enumeration of member roles in a chat."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass
class Member(Entity[MemberId]):
    """
    Member entity representing a participant in a chat.

    A member has a role and can be from the chat.
    """

    id: MemberId
    user_id: str  # Reference to user from IAM context
    chat_id: str  # Reference to chat
    role: MemberRole
    joined_at: datetime
    last_read_at: datetime | None = None

    @classmethod
    @catch_unwrap
    def create(
        cls,
        user_id: str,
        chat_id: str,
        role: MemberRole = MemberRole.MEMBER,
    ) -> Result[Self, VOValidationException]:
        member_id = MemberId.next_id()
        now = utcnow()

        member = cls(
            id=member_id,
            user_id=user_id,
            chat_id=chat_id,
            role=role,
            joined_at=now,
        )

        return Success(member)

    def promote_to_admin(self) -> None:
        """Promote member to admin role."""
        if self.role != MemberRole.OWNER:
            self.role = MemberRole.ADMIN

    def demote_to_member(self) -> None:
        """Demote member to regular member role."""
        if self.role == MemberRole.ADMIN:
            self.role = MemberRole.MEMBER

    def mark_as_read(self) -> None:
        """Mark that the member has read messages up to this point."""
        self.last_read_at = utcnow()

    def is_owner(self) -> bool:
        """Check if member is the chat owner."""
        return self.role == MemberRole.OWNER

    def is_admin(self) -> bool:
        """Check if member is an admin."""
        return self.role == MemberRole.ADMIN

    def has_admin_privileges(self) -> bool:
        """Check if member has admin privileges (owner or admin)."""
        return self.role in [MemberRole.OWNER, MemberRole.ADMIN]

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other) -> bool:
        if isinstance(other, Member):
            return self.id == other.id
        return False
