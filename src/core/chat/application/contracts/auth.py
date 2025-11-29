from typing import Protocol


class AuthService(Protocol):
    """Protocol for authentication service used by chat context.

    This is an Anti-Corruption Layer interface that allows the chat context
    to authenticate users without depending on the IAM context implementation.
    """

    async def auth(self, token: str) -> str | None: ...
