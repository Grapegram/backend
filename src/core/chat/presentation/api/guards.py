from dishka.integrations.litestar import FromDishka, inject
from litestar import Request
from litestar.exceptions import NotAuthorizedException

from src.core.chat.application.contracts.auth import AuthService


@inject
async def get_current_user_id(
    request: Request,
    auth_service: FromDishka[AuthService],
) -> str:
    """
    Dependency that extracts and validates JWT token from Authorization header.

    Returns the authenticated user_id if token is valid.
    Raises NotAuthorizedException if token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise NotAuthorizedException("Missing Authorization header")

    if not auth_header.startswith("Bearer "):
        raise NotAuthorizedException(
            "Invalid Authorization header format. Use 'Bearer <token>'"
        )

    token = auth_header.replace("Bearer ", "").strip()

    user_id = await auth_service.auth(token)

    if not user_id:
        raise NotAuthorizedException("Invalid or expired token")

    return user_id
