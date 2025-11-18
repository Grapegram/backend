from classes import typeclass

from ..entities.user import User


@typeclass
def to_user(instance) -> User:
    """Convert various representations to a User entity in IAM context."""
