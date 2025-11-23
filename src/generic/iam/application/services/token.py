from typing import Protocol

from returns.result import Result

from seedwork.exceptions import FormattedError


class TokenExpiredError(FormattedError):
    _msg_fmt: str = "Token has expired."


class InvalidTokenError(FormattedError):
    _msg_fmt: str = "Token is invalid."


class TokenService(Protocol):
    def verify(
        self, token: str
    ) -> Result[dict, TokenExpiredError | InvalidTokenError]: ...

    def generate(self, payload: dict) -> str: ...
