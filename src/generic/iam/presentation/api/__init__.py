from litestar import Router
from src.generic.iam.presentation.api.Registration import register

from src.generic.iam.presentation.api.login import login

routes = [
    Router(
        path="/auth",
        route_handlers=[
            login,
            register,
        ],
    )
]

__all__ = ["routes"]
