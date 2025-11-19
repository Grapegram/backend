from typing import Protocol


class EmailService(Protocol):
    async def send_verification_email(self, email: str, username: str, token: str) -> None:
        """Send a verification email to the user."""
        ...

    async def send_password_reset_email(self, email: str, username: str, token: str) -> None:
        """Send a password reset email to the user."""
        ...

    async def send_welcome_email(self, email: str, username: str) -> None:
        """Send a welcome email to the user after email verification."""
        ...
