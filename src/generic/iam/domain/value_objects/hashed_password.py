"""
Hashed Password Value Object
"""

from seedwork.domain.value_objects import BoundedString


class HashedPassword(BoundedString):
    """
    Hashed password value object.

    This represents a password that has been securely hashed
    and can be safely stored in the database.

    Examples:
        >>> result = HashedPassword("$2b$12$...")
        >>> hashed = result.unwrap()
        >>> str(hashed)
        '$2b$12$...'

        >>> hashed.algorithm
        'bcrypt'

    Security Note:
        - Always use with proper hashing algorithms (bcrypt, argon2, etc.)
        - Never attempt to unhash or reverse
        - Verify by re-hashing and comparing
    """

    @property
    def algorithm(self) -> str:
        """
        Detect the hashing algorithm used.

        Returns:
            Algorithm name or 'unknown'
        """
        hash_str = str(self._value)

        if (
            hash_str.startswith("$2a$")
            or hash_str.startswith("$2b$")
            or hash_str.startswith("$2y$")
        ):
            return "bcrypt"
        elif hash_str.startswith("$argon2"):
            return "argon2"
        elif hash_str.startswith("$pbkdf2"):
            return "pbkdf2"
        elif hash_str.startswith("$scrypt$"):
            return "scrypt"
        else:
            return "unknown"

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"HashedPassword(algorithm='{self.algorithm}', length={len(self)})"
