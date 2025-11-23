import logging
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class BCryptHasherService:
    """
    Password hashing service using PBKDF2-HMAC from cryptography library.

    Provides secure password hashing and verification using PBKDF2
    with SHA256 algorithm.
    """

    def __init__(self, salt: bytes | None = None, iterations: int = 600_000):
        """
        Initialize hasher service.

        Args:
            salt: Salt for hashing (should be from config in production)
            iterations: Number of iterations for PBKDF2 (default: 600,000)
        """
        self.salt = salt or secrets.token_bytes(16)
        self.iterations = iterations

    def hash(self, plain_text: str) -> str:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.iterations,
        )

        hashed = kdf.derive(plain_text.encode())
        return hashed.hex()

    def verify(self, plain_text: str, hashed_text: str) -> bool:
        try:
            expected_hash = self.hash(plain_text)
            return expected_hash == hashed_text
        except Exception as e:
            logger.warning(f"Password verification failed: {e}")
            return False
