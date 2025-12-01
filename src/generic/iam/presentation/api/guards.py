from dishka.integrations.litestar import FromDishka, inject
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from returns.result import Success

from src.generic.iam.application.services.auth import AuthService


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

    result = await auth_service.auth(token)

    match result:
        case Success():
            user = result.unwrap()
            return str(user.id)
        case _:
            raise NotAuthorizedException("Invalid or expired token")
