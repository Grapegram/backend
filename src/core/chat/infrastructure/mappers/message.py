from seedwork.domain.services.clock import utcnow
from src.core.chat.domain.aggregates import Message
from src.core.chat.domain.mappers import to_message
from src.core.chat.domain.value_objects import ChatId, MessageId, MessageText
from src.core.chat.infrastructure.models import MessageModel


@to_message.instance(MessageModel)
def _to_message_from_model(model: MessageModel) -> Message:
    return Message(
        id=MessageId(model.id),
        chat_id=ChatId(str(model.chat_id)),
        sender_id=model.sender_id,
        text=MessageText.from_raw(model.text) if model.text else None,
        images=model.images if model.images else [],
        sent_at=model.created_at,
        is_deleted=model.is_deleted,
        deleted_at=model.deleted_at,
        edited_at=model.edited_at,
        reactions=model.reactions if model.reactions else {},
        read_by=model.read_by if model.read_by else [],
    )


def message_to_model(message: Message) -> MessageModel:
    now = utcnow()
    return MessageModel(
        id=str(message.id),
        chat_id=str(message.chat_id),
        sender_id=str(message.sender_id),
        text=str(message.text) if message.text else "",
        images=message.images if message.images else [],
        created_at=message.sent_at,
        is_deleted=message.is_deleted,
        deleted_at=message.deleted_at,
        edited_at=message.edited_at,
        reactions=message.reactions if message.reactions else {},
        read_by=message.read_by if message.read_by else [],
        updated_at=now,
    )
