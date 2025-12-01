from dataclasses import dataclass
from datetime import datetime
from typing import Self

from returns.result import Result, Success

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.exceptions import VOValidationException
from seedwork.domain.services.clock import utcnow
from seedwork.returns import catch_unwrap

from .events import (
    UserActivated,
    UserAvatarChanged,
    UserCreated,
    UserDeactivated,
    UserUpdated,
)
from .rules import (
    NewEmailMustBeDifferentFromPreviousEmail,
    NewPasswordMustBeDifferentFromPreviousPassword,
)
from .value_objects import Email, HashedPassword, UserId


@dataclass
class User(AggregateRoot[UserId]):
    """
    User aggregate root representing a user in the IAM context.

    This is an aggregate root that manages user identity and profile information.
    """

    id: UserId
    email: Email
    username: str
    hashed_password: HashedPassword
    avatar: str | None = None
    is_active: bool = True
    is_verified: bool = False
    last_login_at: datetime | None = None

    @classmethod
    @catch_unwrap
    def create(
        cls,
        email: str,
        username: str,
        hashed_password: str,
    ) -> Result[Self, VOValidationException]:
        user_id = UserId.next_id()
        email_vo = Email(email).unwrap()
        hashed_password_vo = HashedPassword(hashed_password).unwrap()
        now = utcnow()

        user = cls(
            id=user_id,
            email=email_vo,
            username=username,
            hashed_password=hashed_password_vo,
        )

        user.register_event(
            UserCreated(
                user_id=user.id,
                email=str(user.email),
                username=user.username,
                created_at=now,
            )
        )

        return Success(user)

    @catch_unwrap
    def change_email(
        self, new_email: str
    ) -> Result[None, NewEmailMustBeDifferentFromPreviousEmail | VOValidationException]:
        email_vo = Email(new_email).unwrap()
        self.check_rule(
            NewEmailMustBeDifferentFromPreviousEmail(
                prev_email=self.email, new_email=email_vo
            )
        ).unwrap()
        self.email = email_vo
        self.is_verified = False  # Require re-verification

        self.register_event(
            UserUpdated(
                user_id=self.id,
                updated_at=self.updated_at,
            )
        )

    @catch_unwrap
    def change_password(
        self, new_hashed_password: str
    ) -> Result[
        None, NewPasswordMustBeDifferentFromPreviousPassword | VOValidationException
    ]:
        password_vo = HashedPassword(new_hashed_password)
        self.check_rule(
            NewPasswordMustBeDifferentFromPreviousPassword(
                prev_password=self.hashed_password, new_password=password_vo
            )
        ).unwrap()
        self.hashed_password = password_vo

        self.register_event(
            UserUpdated(
                user_id=self.id,
                updated_at=self.updated_at,
            )
        )

    def deactivate(self) -> None:
        if not self.is_active:
            return

        self.is_active = False

        self.register_event(
            UserDeactivated(
                user_id=self.id,
                deactivated_at=self.updated_at,
            )
        )

    def activate(self) -> None:
        if self.is_active:
            return

        self.is_active = True

        self.register_event(
            UserActivated(
                user_id=self.id,
                activated_at=self.updated_at,
            )
        )

    def change_avatar(self, new_avatar: str | None) -> None:
        old_avatar = self.avatar
        self.avatar = new_avatar

        self.register_event(
            UserAvatarChanged(
                user_id=self.id,
                old_avatar=old_avatar,
                new_avatar=new_avatar,
                changed_at=utcnow(),
            )
        )

    def verify_email(self) -> None:
        self.is_verified = True

    def record_login(self) -> None:
        self.last_login_at = utcnow()

    def __hash__(self) -> int:
        return hash(self.id)
