from src.generic.iam.domain.aggregates import User
from src.generic.iam.domain.mappers import to_user
from src.generic.iam.domain.value_objects import Email, HashedPassword, UserId
from src.generic.iam.infrastructure.models import UserModel


@to_user.instance(UserModel)
def _to_user_from_model(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=Email.from_raw(model.email),
        username=model.username,
        hashed_password=HashedPassword.from_raw(model.hashed_password),
        is_active=model.is_active,
        is_verified=model.is_verified,
        last_login_at=model.last_login_at,
    )
