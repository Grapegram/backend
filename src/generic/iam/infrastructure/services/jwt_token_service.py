import logging
from datetime import datetime, timedelta
from typing import Any

import jwt
from returns.result import Failure, Result, Success

from ...application.contracts.token import (
    InvalidTokenError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)


class JWTTokenService:
    """
    JWT implementation of TokenService for token generation and verification.

    This service uses PyJWT for creating and verifying JSON Web Tokens.
    It implements the simplified TokenService protocol with just generate() and verify() methods.

    Token expiration times are determined automatically based on the 'type' field in the payload.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60 * 24,  # 24 hours
        refresh_token_expire_minutes: int = 60 * 24 * 7,  # 7 days
        verification_token_expire_minutes: int = 60 * 24,  # 24 hours
        password_reset_token_expire_minutes: int = 60,  # 1 hour
    ):
        """
        Initialize JWT token service.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm to use (default: HS256)
            access_token_expire_minutes: Expiration time for access tokens
            refresh_token_expire_minutes: Expiration time for refresh tokens
            verification_token_expire_minutes: Expiration time for email verification tokens
            password_reset_token_expire_minutes: Expiration time for password reset tokens
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_minutes = refresh_token_expire_minutes
        self.verification_token_expire_minutes = verification_token_expire_minutes
        self.password_reset_token_expire_minutes = password_reset_token_expire_minutes

    def _get_expiration_minutes(self, token_type: str) -> int:
        """
        Get expiration time based on token type.

        Args:
            token_type: Type of token (access_token, refresh_token, email_verification, password_reset)

        Returns:
            Expiration time in minutes
        """
        type_to_expiration = {
            "access_token": self.access_token_expire_minutes,
            "refresh_token": self.refresh_token_expire_minutes,
            "email_verification": self.verification_token_expire_minutes,
            "password_reset": self.password_reset_token_expire_minutes,
        }
        return type_to_expiration.get(token_type, self.access_token_expire_minutes)

    def generate(self, payload: dict[str, Any]) -> str:
        """
        Generate a JWT token from a payload.

        Args:
            payload: Dictionary containing the data to encode.
                     Should include 'type' key to determine expiration time.

        Returns:
            The generated JWT token string

        Example:
            >>> token_service = JWTTokenService(secret_key="my-secret")
            >>> payload = {
            ...     "user_id": "123",
            ...     "email": "user@example.com",
            ...     "type": "access_token"
            ... }
            >>> token = token_service.generate(payload)
        """
        to_encode = payload.copy()

        # Determine expiration based on token type
        token_type = to_encode.get("type", "access_token")
        expire_minutes = self._get_expiration_minutes(token_type)
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)

        # Add standard JWT claims
        to_encode.update(
            {
                "exp": expire,  # Expiration time
                "iat": datetime.utcnow(),  # Issued at
                "nbf": datetime.utcnow(),  # Not before
            }
        )

        # Encode the token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

        logger.debug(
            f"Generated JWT token of type '{token_type}' expiring in {expire_minutes} minutes"
        )

        return encoded_jwt

    def verify(self, token: str) -> Result[dict, TokenExpiredError | InvalidTokenError]:
        """
        Verify and decode a JWT token.

        Args:
            token: The JWT token string to verify

        Returns:
            Result containing the decoded payload dict on success,
            or TokenExpiredError/InvalidTokenError on failure

        Example:
            >>> token_service = JWTTokenService(secret_key="my-secret")
            >>> result = token_service.verify(token)
            >>> match result:
            ...     case Success(payload):
            ...         print(f"User ID: {payload['user_id']}")
            ...     case Failure(TokenExpiredError()):
            ...         print("Token has expired")
            ...     case Failure(InvalidTokenError()):
            ...         print("Token is invalid")
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                },
            )

            logger.debug(
                f"Successfully verified JWT token of type '{payload.get('type', 'unknown')}'"
            )
            return Success(payload)

        except jwt.ExpiredSignatureError:
            logger.warning("Token verification failed: Token has expired")
            return Failure(TokenExpiredError())

        except jwt.InvalidTokenError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return Failure(InvalidTokenError())

        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            return Failure(InvalidTokenError())
