from typing import Protocol


class UserStatusService(Protocol):
    """Protocol for managing user status including online presence and typing indicators.

    Tracks user presence across multiple devices and typing status in chats using Redis with TTL.
    - A user is considered online if they have at least one active device connection
    - Typing status is tracked per chat with short TTL for automatic cleanup
    """

    # Online Status Methods

    async def mark_online(self, user_id: str, device_id: str) -> None:
        """Mark a user's device as online with automatic TTL expiration.

        Args:
            user_id: The user identifier
            device_id: The device/connection identifier
        """
        ...

    async def mark_offline(self, user_id: str, device_id: str) -> None:
        """Mark a user's device as offline immediately.

        Args:
            user_id: The user identifier
            device_id: The device/connection identifier
        """
        ...

    async def refresh_online(self, user_id: str, device_id: str) -> None:
        """Refresh the TTL for a user's device connection.

        Args:
            user_id: The user identifier
            device_id: The device/connection identifier
        """
        ...

    async def is_online(self, user_id: str) -> bool:
        """Check if a user is online on any device.

        Args:
            user_id: The user identifier

        Returns:
            True if the user has at least one active device connection
        """
        ...

    async def get_online_devices(self, user_id: str) -> list[str]:
        """Get all online device IDs for a user.

        Args:
            user_id: The user identifier

        Returns:
            List of device IDs that are currently online
        """
        ...

    async def get_online_users(self, user_ids: list[str]) -> dict[str, bool]:
        """Check online status for multiple users efficiently.

        Args:
            user_ids: List of user identifiers to check

        Returns:
            Dictionary mapping user_id to online status
        """
        ...

    # Typing Indicator Methods

    async def start_typing(self, user_id: str, chat_id: str) -> None:
        """Mark a user as typing in a specific chat.

        Sets a short TTL (e.g., 3-5 seconds) that requires frequent refresh.
        Automatically expires if user stops typing or disconnects.

        Args:
            user_id: The user identifier
            chat_id: The chat identifier where user is typing
        """
        ...

    async def stop_typing(self, user_id: str, chat_id: str) -> None:
        """Remove typing indicator for a user in a specific chat.

        Args:
            user_id: The user identifier
            chat_id: The chat identifier
        """
        ...

    async def get_typing_users(self, chat_id: str) -> list[str]:
        """Get list of users currently typing in a chat.

        Args:
            chat_id: The chat identifier

        Returns:
            List of user IDs currently typing in the chat
        """
        ...

    async def is_typing(self, user_id: str, chat_id: str) -> bool:
        """Check if a specific user is typing in a chat.

        Args:
            user_id: The user identifier
            chat_id: The chat identifier

        Returns:
            True if the user is currently typing in the chat
        """
        ...


# Keep old name for backward compatibility
OnlineStatusService = UserStatusService
