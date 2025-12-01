"""
Chat Business Rules

Business rules that govern the Chat aggregate behavior.
"""

from dataclasses import dataclass

from seedwork.domain.rule import BusinessRule

from ..entities import Member


@dataclass
class OnlyAdminCanChangeChatTitle(BusinessRule):
    """Only admins or owners can change the chat title."""

    member: Member

    def is_broken(self) -> bool:
        return not self.member.has_admin_privileges()


@dataclass
class OnlyAdminCanChangeChatAvatar(BusinessRule):
    """Only admins or owners can change the chat avatar."""

    member: Member

    def is_broken(self) -> bool:
        return not self.member.has_admin_privileges()


@dataclass
class OnlyAdminCanAddMembers(BusinessRule):
    """Only admins or owners can add members to the chat."""

    member: Member

    def is_broken(self) -> bool:
        return not self.member.has_admin_privileges()


@dataclass
class OnlyAdminCanRemoveMembers(BusinessRule):
    """Only admins or owners can remove members from the chat."""

    member: Member

    def is_broken(self) -> bool:
        return not self.member.has_admin_privileges()


@dataclass
class OnlyOwnerCanChangeOwnership(BusinessRule):
    """Only the owner can transfer ownership."""

    member: Member

    def is_broken(self) -> bool:
        return not self.member.is_owner()


@dataclass
class CannotRemoveOwner(BusinessRule):
    """The owner cannot be removed from the chat."""

    member_to_remove: Member

    def is_broken(self) -> bool:
        return self.member_to_remove.is_owner()


@dataclass
class ChatMustHaveAtLeastOneMember(BusinessRule):
    """A chat must have at least one member."""

    member_count: int

    def is_broken(self) -> bool:
        return self.member_count < 1


@dataclass
class MemberMustNotAlreadyExist(BusinessRule):
    """This user is already a member of the chat."""

    user_id: str
    existing_member_user_ids: list[str]

    def is_broken(self) -> bool:
        return self.user_id in self.existing_member_user_ids
