from seedwork.domain.services.clock import utcnow
from src.core.chat.domain.aggregates import Chat
from src.core.chat.domain.entities import Member, MemberRole
from src.core.chat.domain.mappers import to_chat
from src.core.chat.domain.value_objects import ChatId, ChatTitle, MemberId
from src.core.chat.infrastructure.models import ChatModel, MemberModel


def _model_to_member(model: MemberModel) -> Member:
    return Member(
        id=MemberId(str(model.id)),
        user_id=model.user_id,
        chat_id=str(model.chat_id),
        role=MemberRole(model.role),
        joined_at=model.joined_at,
        last_read_at=model.last_read_at,
    )


@to_chat.instance(ChatModel)
def _to_chat_from_model(model: ChatModel) -> Chat:
    members = [_model_to_member(member_model) for member_model in model.members]

    avatar = str.create(model.avatar).unwrap() if model.avatar else None

    return Chat(
        id=ChatId(str(model.id)),
        title=ChatTitle.from_raw(model.title),
        avatar=avatar,
        is_archived=model.is_archived,
        archived_at=model.archived_at,
        members=members,
    )


def member_to_model(member: Member, chat_id: ChatId) -> MemberModel:
    return MemberModel(
        id=str(member.id),
        user_id=str(member.user_id),
        chat_id=str(chat_id),
        role=member.role.value,
        joined_at=member.joined_at,
        last_read_at=member.last_read_at,
    )


def chat_to_model(chat: Chat) -> ChatModel:
    now = utcnow()
    return ChatModel(
        id=str(chat.id),
        title=str(chat.title),
        avatar=chat.avatar,
        is_archived=chat.is_archived,
        archived_at=chat.archived_at,
        created_at=now,
        updated_at=now,
    )
