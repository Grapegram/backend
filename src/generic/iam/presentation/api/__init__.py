from litestar import Router

from src.generic.iam.presentation.api.change_user_avatar import (
    delete_user_avatar,
    upload_user_avatar,
)
from src.generic.iam.presentation.api.get_current_user import get_current_user
from src.generic.iam.presentation.api.get_users_list import get_users_list
from src.generic.iam.presentation.api.login import login
from src.generic.iam.presentation.api.registration import register
from src.generic.iam.presentation.api.verification_email import verify_email

routes = [
    Router(
        path="/auth",
        route_handlers=[
            login,
            register,
            verify_email,
        ],
    ),
    Router(
        path="/users",
        route_handlers=[
            Router(
                path="/me",
                route_handlers=[
                    get_current_user,
                    upload_user_avatar,
                    delete_user_avatar,
                ],
            ),
            get_users_list,
        ],
    ),
]


__all__ = ["routes"]
