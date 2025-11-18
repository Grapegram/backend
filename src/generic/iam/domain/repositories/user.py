from seedwork.domain.repositories import Repository

from ..entities.user import User
from ..value_objects.user_id import UserId


class UserRepository(Repository[UserId, User]): ...
