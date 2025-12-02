from litestar import Router

from src.core.chat.presentation.api.add_member import add_member
from src.core.chat.presentation.api.add_reaction import add_reaction
from src.core.chat.presentation.api.archive_chat import archive_chat, unarchive_chat
from src.core.chat.presentation.api.change_chat_avatar import (
    delete_chat_avatar,
    upload_chat_avatar,
)
from src.core.chat.presentation.api.change_chat_title import change_chat_title
from src.core.chat.presentation.api.chat_ws import live_chat
from src.core.chat.presentation.api.create_chat import create_chat
from src.core.chat.presentation.api.delete_chat import delete_chat
from src.core.chat.presentation.api.delete_message import delete_message
from src.core.chat.presentation.api.edit_message import edit_message
from src.core.chat.presentation.api.get_chats_list import get_chats_list
from src.core.chat.presentation.api.load_messages import load_messages
from src.core.chat.presentation.api.send_message import send_message

routes = [
    Router(
        path="",
        route_handlers=[
            # Chat operations
            create_chat,
            get_chats_list,
            change_chat_title,
            upload_chat_avatar,
            delete_chat_avatar,
            archive_chat,
            unarchive_chat,
            delete_chat,
            # Member operations
            add_member,
            # Message operations
            send_message,
            load_messages,
            edit_message,
            delete_message,
            # Reaction operations
            add_reaction,
            live_chat,
        ],
    ),
]


__all__ = ["routes"]
