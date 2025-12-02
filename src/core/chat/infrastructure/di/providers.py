from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from seedwork.application.event_bus import EventBus
from seedwork.application.notifier import Notifier
from seedwork.application.object_storage import ObjectStorage
from src.core.chat.application.contracts.auth import AuthService
from src.core.chat.application.contracts.repositories import ChatReadRepository
from src.core.chat.application.handlers.events import ExposeMessageSentEvent
from src.core.chat.application.handlers.queries import (
    GetChatsList,
    LoadMessagesFromChat,
)
from src.core.chat.application.services.chat import ChatService
from src.core.chat.application.services.message import MessageService
from src.core.chat.application.use_cases import (
    AddMember,
    AddReaction,
    ArchiveChat,
    ChangeChatAvatar,
    ChangeChatTitle,
    ChangeMemberRole,
    CreateChat,
    DeleteChat,
    DeleteMessage,
    EditMessage,
    MarkMessageAsRead,
    RemoveMember,
    RemoveReaction,
    SendMessage,
    UnarchiveChat,
)
from src.core.chat.domain.repositories import ChatRepository, MessageRepository
from src.core.chat.infrastructure.acl.auth import IAMAuthServiceACL
from src.core.chat.infrastructure.repositories import (
    SQLAlchemyChatReadRepository,
    SQLAlchemyChatRepository,
    SQLAlchemyMessageRepository,
)
from src.generic.iam.application.services.auth import AuthService as IAMAuthService


class ChatProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_chat_service(self, object_storage: ObjectStorage) -> ChatService:
        return ChatService(object_storage=object_storage)

    @provide(scope=Scope.APP)
    def provide_message_service(self, object_storage: ObjectStorage) -> MessageService:
        return MessageService(object_storage=object_storage)

    @provide(scope=Scope.REQUEST)
    def provide_chat_repository(self, session: AsyncSession) -> ChatRepository:
        return SQLAlchemyChatRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_message_repository(self, session: AsyncSession) -> MessageRepository:
        return SQLAlchemyMessageRepository(session)

    @provide(scope=Scope.REQUEST)
    def provide_chat_read_repository(
        self, session: AsyncSession, object_storage: ObjectStorage
    ) -> ChatReadRepository:
        return SQLAlchemyChatReadRepository(session, object_storage)

    @provide(scope=Scope.REQUEST)
    def provide_get_chats_list_handler(
        self,
        chat_read_repo: ChatReadRepository,
    ) -> GetChatsList:
        return GetChatsList(chat_read_repo=chat_read_repo)

    @provide(scope=Scope.REQUEST)
    def provide_load_messages_from_chat_handler(
        self,
        chat_read_repo: ChatReadRepository,
    ) -> LoadMessagesFromChat:
        return LoadMessagesFromChat(chat_read_repo=chat_read_repo)

    @provide(scope=Scope.REQUEST)
    def provide_expose_message_sent_event_handler(
        self,
        notifier: Notifier,
    ) -> ExposeMessageSentEvent:
        return ExposeMessageSentEvent(notifier=notifier)

    @provide(scope=Scope.REQUEST)
    def provide_auth_service(
        self,
        iam_auth: IAMAuthService,
    ) -> AuthService:
        return IAMAuthServiceACL(iam_auth=iam_auth)

    @provide(scope=Scope.REQUEST)
    def provide_create_chat_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> CreateChat:
        return CreateChat(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_change_chat_title_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> ChangeChatTitle:
        return ChangeChatTitle(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_change_chat_avatar_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
        chat_service: ChatService,
    ) -> ChangeChatAvatar:
        return ChangeChatAvatar(
            chat_repo=chat_repo,
            event_bus=event_bus,
            chat_service=chat_service,
        )

    @provide(scope=Scope.REQUEST)
    def provide_add_member_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> AddMember:
        return AddMember(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_remove_member_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> RemoveMember:
        return RemoveMember(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_change_member_role_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> ChangeMemberRole:
        return ChangeMemberRole(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_archive_chat_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> ArchiveChat:
        return ArchiveChat(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_unarchive_chat_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> UnarchiveChat:
        return UnarchiveChat(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_delete_chat_story(
        self,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> DeleteChat:
        return DeleteChat(
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_send_message_story(
        self,
        message_repo: MessageRepository,
        message_service: MessageService,
        event_bus: EventBus,
    ) -> SendMessage:
        return SendMessage(
            message_repo=message_repo,
            message_service=message_service,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_edit_message_story(
        self,
        message_repo: MessageRepository,
        event_bus: EventBus,
    ) -> EditMessage:
        return EditMessage(
            message_repo=message_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_delete_message_story(
        self,
        message_repo: MessageRepository,
        chat_repo: ChatRepository,
        event_bus: EventBus,
    ) -> DeleteMessage:
        return DeleteMessage(
            message_repo=message_repo,
            chat_repo=chat_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_add_reaction_story(
        self,
        message_repo: MessageRepository,
        event_bus: EventBus,
    ) -> AddReaction:
        return AddReaction(
            message_repo=message_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_remove_reaction_story(
        self,
        message_repo: MessageRepository,
        event_bus: EventBus,
    ) -> RemoveReaction:
        return RemoveReaction(
            message_repo=message_repo,
            event_bus=event_bus,
        )

    @provide(scope=Scope.REQUEST)
    def provide_mark_message_as_read_story(
        self,
        message_repo: MessageRepository,
        event_bus: EventBus,
    ) -> MarkMessageAsRead:
        return MarkMessageAsRead(
            message_repo=message_repo,
            event_bus=event_bus,
        )
