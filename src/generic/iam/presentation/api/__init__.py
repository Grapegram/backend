from litestar import Router

from src.generic.iam.presentation.api.login import login
from src.generic.iam.presentation.api.registration import register

routes = [
    Router(
        path="/auth",
        route_handlers=[
            login,
            register,
        ],
    ),
]


__all__ = ["routes"]
