from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

from returns.result import Result, Success

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.services.clock import utcnow
from seedwork.returns import catch_unwrap

from ..entities import Member, MemberRole
from ..events import (
    ChatArchived,
    ChatAvatarChanged,
    ChatCreated,
    ChatTitleChanged,
    ChatUnarchived,
    MemberAdded,
    MemberRemoved,
    MemberRoleChanged,
)
from ..rules.chat import (
    CannotRemoveOwner,
    ChatMustHaveAtLeastOneMember,
    MemberMustNotAlreadyExist,
    OnlyAdminCanAddMembers,
    OnlyAdminCanChangeChatAvatar,
    OnlyAdminCanChangeChatTitle,
    OnlyAdminCanRemoveMembers,
    OnlyOwnerCanChangeOwnership,
    UserIsNotMember,
)
from ..value_objects import ChatId, ChatTitle


@dataclass
class Chat(AggregateRoot[ChatId]):
    """
    Chat aggregate root representing a conversation.

    This is an aggregate root that manages chat metadata, members,
    and ensures business rules are enforced.
    """

    id: ChatId
    title: ChatTitle
    avatar: str | None = None
    is_archived: bool = False
    archived_at: datetime | None = None
    members: list[Member] = field(default_factory=list)

    @classmethod
    @catch_unwrap
    def create(
        cls,
        title: str,
        created_by: str,
    ) -> Result[Self, VOValidationException]:
        chat_id = ChatId.next_id()
        title_vo = ChatTitle(title).unwrap()
        now = utcnow()

        # Create the owner member
        owner = Member.create(
            user_id=created_by,
            chat_id=str(chat_id),
            role=MemberRole.OWNER,
        ).unwrap()

        chat = cls(
            id=chat_id,
            title=title_vo,
            members=[owner],
        )

        chat.register_event(
            ChatCreated(
                chat_id=chat_id,
                title=str(title_vo),
                created_by=created_by,
                created_at=now,
            )
        )

        chat.register_event(
            MemberAdded(
                chat_id=chat_id,
                member_id=str(owner.id),
                user_id=created_by,
                role=MemberRole.OWNER.value,
                added_by=created_by,
                added_at=now,
            )
        )

        return Success(chat)

    @catch_unwrap
    def change_title(
        self, new_title: str, changed_by: str
    ) -> Result[None, VOValidationException]:
        self.check_rule(
            UserIsNotMember(members=self.members, user_id=changed_by)
        ).unwrap()
        member = self._get_member_by_user_id(changed_by)

        self.check_rule(OnlyAdminCanChangeChatTitle(member=member)).unwrap()

        title_vo = ChatTitle(new_title).unwrap()
        old_title = str(self.title)
        self.title = title_vo

        self.register_event(
            ChatTitleChanged(
                chat_id=self.id,
                old_title=old_title,
                new_title=str(title_vo),
                changed_by=changed_by,
                changed_at=utcnow(),
            )
        )
        return Success(None)

    @catch_unwrap
    def change_avatar(
        self, new_avatar: str | None, changed_by: str
    ) -> Result[None, VOValidationException]:
        self.check_rule(
            UserIsNotMember(members=self.members, user_id=changed_by)
        ).unwrap()
        member = self._get_member_by_user_id(changed_by)
        self.check_rule(OnlyAdminCanChangeChatAvatar(member=member)).unwrap()

        old_avatar = self.avatar
        self.avatar = new_avatar

        self.register_event(
            ChatAvatarChanged(
                chat_id=self.id,
                old_avatar=old_avatar,
                new_avatar=new_avatar,
                changed_by=changed_by,
                changed_at=utcnow(),
            )
        )

        return Success(None)

    @catch_unwrap
    def add_member(
        self, user_id: str, added_by: str, role: MemberRole = MemberRole.MEMBER
    ) -> Result[Member, VOValidationException]:
        self.check_rule(
            UserIsNotMember(members=self.members, user_id=added_by)
        ).unwrap()
        member = self._get_member_by_user_id(added_by)
        self.check_rule(OnlyAdminCanAddMembers(member=member)).unwrap()

        existing_user_ids = [m.user_id for m in self.members]
        self.check_rule(
            MemberMustNotAlreadyExist(
                user_id=user_id, existing_member_user_ids=existing_user_ids
            )
        ).unwrap()

        new_member = Member.create(
            user_id=user_id,
            chat_id=str(self.id),
            role=role,
        ).unwrap()

        self.members.append(new_member)

        self.register_event(
            MemberAdded(
                chat_id=self.id,
                member_id=str(new_member.id),
                user_id=user_id,
                role=role.value,
                added_by=added_by,
                added_at=utcnow(),
            )
        )

        return Success(new_member)

    @catch_unwrap
    def remove_member(
        self, user_id: str, removed_by: str
    ) -> Result[None, VOValidationException]:
        self.check_rule(
            UserIsNotMember(members=self.members, user_id=removed_by)
        ).unwrap()
        member = self._get_member_by_user_id(removed_by)

        self.check_rule(UserIsNotMember(members=self.members, user_id=user_id)).unwrap()
        member_to_remove = self._get_member_by_user_id(user_id)

        # User can remove themselves, or admin can remove others
        if user_id != removed_by:
            self.check_rule(OnlyAdminCanRemoveMembers(member=member)).unwrap()

        self.check_rule(CannotRemoveOwner(member_to_remove=member_to_remove)).unwrap()
        self.check_rule(
            ChatMustHaveAtLeastOneMember(member_count=len(self.members) - 1)
        ).unwrap()

        self.members = [m for m in self.members if m.user_id != user_id]

        self.register_event(
            MemberRemoved(
                chat_id=self.id,
                member_id=str(member_to_remove.id),
                user_id=user_id,
                removed_by=removed_by,
                removed_at=utcnow(),
            )
        )
        return Success(None)

    @catch_unwrap
    def change_member_role(
        self, user_id: str, new_role: MemberRole, changed_by: str
    ) -> Result[None, VOValidationException]:
        self.check_rule(
            UserIsNotMember(members=self.members, user_id=changed_by)
        ).unwrap()
        member = self._get_member_by_user_id(changed_by)

        self.check_rule(UserIsNotMember(members=self.members, user_id=user_id)).unwrap()
        member = self._get_member_by_user_id(user_id)

        # Only owner can change ownership
        if new_role == MemberRole.OWNER:
            self.check_rule(OnlyOwnerCanChangeOwnership(member=member)).unwrap()
        else:
            self.check_rule(OnlyAdminCanAddMembers(member=member)).unwrap()

        old_role = member.role

        if new_role == old_role:
            return  # No change needed

        if new_role == MemberRole.OWNER:
            # Transfer ownership: demote current owner to admin
            current_owner = self._get_owner()
            if current_owner:
                current_owner.demote_to_member()
                current_owner.promote_to_admin()

        member.role = new_role

        self.register_event(
            MemberRoleChanged(
                chat_id=self.id,
                member_id=str(member.id),
                old_role=old_role.value,
                new_role=new_role.value,
                changed_by=changed_by,
                changed_at=utcnow(),
            )
        )
        return Success(None)

    @catch_unwrap
    def archive(self, archived_by: str) -> None:
        if self.is_archived:
            return

        self.check_rule(
            UserIsNotMember(members=self.members, user_id=archived_by)
        ).unwrap()
        member = self._get_member_by_user_id(archived_by)

        if not member.has_admin_privileges():
            raise ValueError("Only admins or owners can archive the chat")

        self.is_archived = True
        self.archived_at = utcnow()

        self.register_event(
            ChatArchived(
                chat_id=self.id,
                archived_by=archived_by,
                archived_at=self.archived_at,
            )
        )
        return Success(None)

    @catch_unwrap
    def unarchive(self, unarchived_by: str) -> None:
        if not self.is_archived:
            return

        self.check_rule(
            UserIsNotMember(members=self.members, user_id=unarchived_by)
        ).unwrap()
        member = self._get_member_by_user_id(unarchived_by)

        if not member.has_admin_privileges():
            raise ValueError("Only admins or owners can unarchive the chat")

        self.is_archived = False
        self.archived_at = None

        self.register_event(
            ChatUnarchived(
                chat_id=self.id,
                unarchived_by=unarchived_by,
                unarchived_at=utcnow(),
            )
        )

        return Success(None)

    def owner(self) -> Member:
        for member in self.members:
            if member.is_owner():
                return member
        raise RuntimeError("Chat has no owner")

    def get_member(self, user_id: str) -> Member | None:
        return self._get_member_by_user_id(user_id)

    def has_member(self, user_id: str) -> bool:
        return self._get_member_by_user_id(user_id) is not None

    def get_member_count(self) -> int:
        return len(self.members)

    def _get_member_by_user_id(self, user_id: str) -> Member | None:
        for member in self.members:
            if member.user_id == user_id:
                return member
        return None
