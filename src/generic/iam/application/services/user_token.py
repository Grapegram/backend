from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from returns.result import Failure, Result, Success

from ...domain.aggregates import User
from ..contracts.token import InvalidTokenError, TokenExpiredError, TokenService


class InvalidTokenTypeError(Exception):
    """Raised when token type doesn't match expected type."""

    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Expected token type '{expected}', got '{actual}'")


@dataclass
class UserTokenPayload:
    """Parsed and validated user token payload."""

    user_id: str
    email: str
    username: str | None = None
    is_verified: bool | None = None
    token_type: str = "access_token"
    issued_at: datetime | None = None
    expires_at: datetime | None = None


class TokenTypeStrategy(ABC):
    """
    Abstract strategy for token type-specific operations.

    Each token type (login, verification, password reset, refresh) implements
    this strategy to define how its payload is built and validated.
    """

    @property
    @abstractmethod
    def token_type(self) -> str:
        """The token type identifier (e.g., 'access_token', 'email_verification')."""
        pass

    @abstractmethod
    def build_payload(self, user: User) -> dict:
        """
        Build the token payload for this token type.
        """

    def validate_payload(self, payload_dict: dict) -> None:
        """
        Validate token payload for this specific token type.
        """


class LoginTokenStrategy(TokenTypeStrategy):
    """Strategy for access/login tokens with full user information."""

    @property
    def token_type(self) -> str:
        return "access_token"

    def build_payload(self, user: User) -> dict:
        return {
            "user_id": str(user.id),
            "email": str(user.email),
            "username": user.username,
            "is_verified": user.is_verified,
            "is_active": user.is_active,
            "type": self.token_type,
        }

    def validate_payload(self, payload_dict: dict) -> None:
        """Validate that login token has required fields."""
        required_fields = ["user_id", "email", "username", "is_verified"]
        missing = [f for f in required_fields if f not in payload_dict]
        if missing:
            raise ValueError(f"Missing required fields for login token: {missing}")


@dataclass(frozen=True)
class VerificationTokenPayload:
    user_id: str
    email: str


class VerificationTokenStrategy(TokenTypeStrategy):
    """Strategy for email verification tokens with minimal claims."""

    @property
    def token_type(self) -> str:
        return "email_verification"

    def build_payload(self, user: VerificationTokenPayload) -> dict:
        return {
            "user_id": str(user.user_id),
            "email": str(user.email),
            "type": self.token_type,
        }

    def validate_payload(self, payload_dict: dict) -> None:
        """Validate that verification token has minimal required fields."""
        required_fields = ["user_id", "email"]
        missing = [f for f in required_fields if f not in payload_dict]
        if missing:
            raise ValueError(
                f"Missing required fields for verification token: {missing}"
            )


class PasswordResetTokenStrategy(TokenTypeStrategy):
    """Strategy for password reset tokens with minimal claims and short expiration."""

    @property
    def token_type(self) -> str:
        return "password_reset"

    def build_payload(self, user: User) -> dict:
        return {
            "user_id": str(user.id),
            "email": str(user.email),
            "type": self.token_type,
        }

    def validate_payload(self, payload_dict: dict) -> None:
        """Validate that password reset token has required fields."""
        required_fields = ["user_id", "email"]
        missing = [f for f in required_fields if f not in payload_dict]
        if missing:
            raise ValueError(
                f"Missing required fields for password reset token: {missing}"
            )


class RefreshTokenStrategy(TokenTypeStrategy):
    """Strategy for refresh tokens with minimal claims for security."""

    @property
    def token_type(self) -> str:
        return "refresh_token"

    def build_payload(self, user: User) -> dict:
        return {
            "user_id": str(user.id),
            "type": self.token_type,
        }

    def validate_payload(self, payload_dict: dict) -> None:
        """Validate that refresh token has required fields."""
        if "user_id" not in payload_dict:
            raise ValueError("Missing required field 'user_id' for refresh token")


class UserTokenService:
    """
    Domain-specific service for creating and verifying user tokens.

    Uses Strategy pattern with a clean, explicit API where strategies are passed directly.

    Example:
        >>> tokens = UserTokenService(token_service)
        >>> token = tokens.create(LoginTokenStrategy, user)
        >>> payload = tokens.verify(LoginTokenStrategy, token)
    """

    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    def _get_strategy_instance(
        self, strategy: type[TokenTypeStrategy] | TokenTypeStrategy
    ) -> TokenTypeStrategy:
        if isinstance(strategy, type):
            return strategy()
        return strategy

    def create(
        self, strategy: type[TokenTypeStrategy] | TokenTypeStrategy, user: User
    ) -> str:
        strategy_instance = self._get_strategy_instance(strategy)
        payload = strategy_instance.build_payload(user)
        return self.token_service.generate(payload)

    def verify(
        self, strategy: type[TokenTypeStrategy] | TokenTypeStrategy, token: str
    ) -> Result[
        UserTokenPayload, TokenExpiredError | InvalidTokenError | InvalidTokenTypeError
    ]:
        strategy_instance = self._get_strategy_instance(strategy)
        expected_type = strategy_instance.token_type

        verification_result = self.token_service.verify(token)

        match verification_result:
            case Failure(error):
                return Failure(error)
            case Success(payload_dict):
                return self._process_verified_payload(
                    payload_dict, expected_type, strategy_instance
                )

    def _process_verified_payload(
        self,
        payload_dict: dict,
        expected_type: str,
        strategy: TokenTypeStrategy,
    ) -> Result[UserTokenPayload, InvalidTokenError | InvalidTokenTypeError]:
        token_type = payload_dict.get("type", "access_token")

        # Check token type matches expected
        if token_type != expected_type:
            return Failure(InvalidTokenTypeError(expected_type, token_type))

        # Validate with strategy
        try:
            strategy.validate_payload(payload_dict)
        except ValueError:
            return Failure(InvalidTokenError())

        try:
            user_payload = self._parse_payload(payload_dict)
            return Success(user_payload)
        except (KeyError, ValueError):
            return Failure(InvalidTokenError())

    def _parse_payload(self, payload_dict: dict) -> UserTokenPayload:
        issued_at = None
        if "iat" in payload_dict:
            issued_at = datetime.fromtimestamp(payload_dict["iat"])

        expires_at = None
        if "exp" in payload_dict:
            expires_at = datetime.fromtimestamp(payload_dict["exp"])

        return UserTokenPayload(
            user_id=payload_dict["user_id"],
            email=payload_dict["email"],
            username=payload_dict.get("username"),
            is_verified=payload_dict.get("is_verified"),
            token_type=payload_dict.get("type", "access_token"),
            issued_at=issued_at,
            expires_at=expires_at,
        )
