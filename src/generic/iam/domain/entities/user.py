from dataclasses import dataclass, field
from datetime import datetime

from seedwork.domain.entities import AggregateRoot
from seedwork.domain.services import utcnow
from seedwork.domain.value_objects import Email

from ..events import UserActivated, UserCreated, UserDeactivated, UserUpdated
from ..value_objects import UserId


@dataclass
class User(AggregateRoot[UserId]):
    """
    User aggregate root representing a user in the IAM context.

    This is an aggregate root that manages user identity and profile information.
    """

    id: UserId
    email: Email
    username: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    last_login_at: datetime | None = None

    @classmethod
    def create(
        cls,
        email: str,
        username: str,
        hashed_password: str,
    ) -> "User":
        """
        Factory method to create a new user.

        Args:
            email: User's email address
            username: User's unique username
            hashed_password: Pre-hashed password

        Returns:
            New User instance with UserCreated event
        """
        user_id = UserId.next_id()
        email_vo = Email(email)
        now = utcnow()

        user = cls(
            id=user_id,
            email=email_vo,
            username=username,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
        )

        user.register_event(
            UserCreated(
                user_id=user_id,
                email=email,
                username=username,
                created_at=now,
            )
        )

        return user

    def change_email(self, new_email: str) -> None:
        """
        Change user's email address.

        Args:
            new_email: New email address
        """
        self.email = Email(new_email)
        self.is_verified = False  # Require re-verification
        self.updated_at = utcnow()

        self.register_event(
            UserUpdated(
                user_id=self.id,
                updated_at=self.updated_at,
            )
        )

    def change_password(self, new_hashed_password: str) -> None:
        """
        Change user's password.

        Args:
            new_hashed_password: New pre-hashed password
        """
        self.hashed_password = new_hashed_password
        self.updated_at = utcnow()

        self.register_event(
            UserUpdated(
                user_id=self.id,
                updated_at=self.updated_at,
            )
        )

    def deactivate(self) -> None:
        """Deactivate the user account."""
        if not self.is_active:
            return

        self.is_active = False
        self.updated_at = utcnow()

        self.register_event(
            UserDeactivated(
                user_id=self.id,
                deactivated_at=self.updated_at,
            )
        )

    def activate(self) -> None:
        """Activate the user account."""
        if self.is_active:
            return

        self.is_active = True
        self.updated_at = utcnow()

        self.register_event(
            UserActivated(
                user_id=self.id,
                activated_at=self.updated_at,
            )
        )

    def verify_email(self) -> None:
        """Mark user's email as verified."""
        self.is_verified = True
        self.updated_at = utcnow()

    def record_login(self) -> None:
        """Record user's last login timestamp."""
        self.last_login_at = utcnow()

    def __hash__(self) -> int:
        return hash(self.id)
