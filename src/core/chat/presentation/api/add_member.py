from typing import Annotated

from dishka.integrations.litestar import FromDishka, inject
from litestar import post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from msgspec import Struct
from returns.result import Failure, Success
from stories import State

from src.core.chat.application.use_cases.add_member import AddMember, FailedStatuses
from src.core.chat.domain.entities import MemberRole
from src.core.chat.presentation.api.guards import get_current_user_id


class AddMemberRequest(Struct):
    chat_id: str
    user_id: str
    role: str = "member"


class AddMemberResponse(Struct):
    member_id: str
    user_id: str
    chat_id: str
    role: str


@post(
    "/chats/members",
    status_code=HTTP_201_CREATED,
    summary="Add member to chat",
    description="Add a new member to an existing chat",
    dependencies={"current_user": Provide(get_current_user_id)},
    security=[{"IAMTokenAuth": []}],
)
@inject
async def add_member(
    data: Annotated[AddMemberRequest, Body(media_type=RequestEncodingType.JSON)],
    story: FromDishka[AddMember],
    current_user: str,
) -> AddMemberResponse:
    try:
        role = MemberRole(data.role)
    except ValueError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be one of: owner, admin, member",
        )

    state = State(
        chat_id=data.chat_id,
        user_id=data.user_id,
        added_by=current_user,
        role=role,
    )
    await story(state)

    match state.result:
        case Success(member):
            return AddMemberResponse(
                member_id=str(member.id),
                user_id=member.user_id,
                chat_id=member.chat_id,
                role=member.role.value,
            )
        case Failure(error_status):
            error_messages = {
                FailedStatuses.CHAT_NOT_FOUND: "Chat not found",
                FailedStatuses.ACTOR_NOT_MEMBER: "You are not a member of this chat",
                FailedStatuses.INSUFFICIENT_PERMISSIONS: "Only admins can add members",
                FailedStatuses.MEMBER_ALREADY_EXISTS: "User is already a member of this chat",
                FailedStatuses.INVALID_INPUT: "Invalid member data",
            }

            status_code = (
                HTTP_403_FORBIDDEN
                if error_status
                in [
                    FailedStatuses.INSUFFICIENT_PERMISSIONS,
                    FailedStatuses.ACTOR_NOT_MEMBER,
                ]
                else HTTP_400_BAD_REQUEST
            )

            raise HTTPException(
                status_code=status_code,
                detail=error_messages.get(error_status, "Failed to add member"),
                extra={"error_code": error_status.value},
            )
