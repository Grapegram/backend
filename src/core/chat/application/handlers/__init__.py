from .events import (
    ExposeChatDeletedEvent,
    ExposeMemberAddedEvent,
    ExposeMessageDeletedEvent,
    ExposeMessageSentEvent,
)
from .queries.load_messages_from_chat import LoadMessagesFromChat
from .user_status_handlers import (
    HandleUserOffline,
    HandleUserOnline,
    HandleUserTypingStarted,
    HandleUserTypingStopped,
)

handlers = [
    # events
    ExposeMessageSentEvent,
    ExposeMemberAddedEvent,
    ExposeChatDeletedEvent,
    ExposeMessageDeletedEvent,
    # user status events
    HandleUserOnline,
    HandleUserOffline,
    HandleUserTypingStarted,
    HandleUserTypingStopped,
    # queries
    LoadMessagesFromChat,
]

__all__ = ["handlers"]
