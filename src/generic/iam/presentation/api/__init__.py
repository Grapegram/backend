from litestar import Router

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
]


__all__ = ["routes"]
