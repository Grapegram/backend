from redis.asyncio import Redis


class RedisUserStatusService:
    """Redis-based implementation for tracking user status (online and typing).

    Uses Redis keys with TTL to automatically expire connections and typing indicators.
    Key patterns:
    - Online: online:{user_id}:{device_id}
    - Typing: typing:{chat_id}:{user_id}
    """

    def __init__(
        self,
        redis: Redis,
        online_ttl_seconds: int = 30,
        typing_ttl_seconds: int = 5,
    ):
        self._redis = redis
        self._online_ttl_seconds = online_ttl_seconds
        self._typing_ttl_seconds = typing_ttl_seconds

    # Online status key helpers
    def _device_key(self, user_id: str, device_id: str) -> str:
        return f"online:{user_id}:{device_id}"

    def _user_pattern(self, user_id: str) -> str:
        return f"online:{user_id}:*"

    # Typing indicator key helpers
    def _typing_key(self, user_id: str, chat_id: str) -> str:
        return f"typing:{chat_id}:{user_id}"

    def _typing_pattern(self, chat_id: str) -> str:
        return f"typing:{chat_id}:*"

    # Online Status Methods
    async def mark_online(self, user_id: str, device_id: str) -> None:
        key = self._device_key(user_id, device_id)
        await self._redis.setex(key, self._online_ttl_seconds, "1")

    async def mark_offline(self, user_id: str, device_id: str) -> None:
        key = self._device_key(user_id, device_id)
        await self._redis.delete(key)

    async def refresh_online(self, user_id: str, device_id: str) -> None:
        key = self._device_key(user_id, device_id)
        await self._redis.expire(key, self._online_ttl_seconds)

    async def is_online(self, user_id: str) -> bool:
        pattern = self._user_pattern(user_id)

        async for key in self._redis.scan_iter(match=pattern, count=100):
            return True

        return False

    async def get_online_devices(self, user_id: str) -> list[str]:
        pattern = self._user_pattern(user_id)
        devices = []

        async for key in self._redis.scan_iter(match=pattern, count=100):
            key_str = key.decode("utf-8") if isinstance(key, bytes) else key
            device_id = key_str.split(":")[-1]
            devices.append(device_id)

        return devices

    async def get_online_users(self, user_ids: list[str]) -> dict[str, bool]:
        result = {}

        for user_id in user_ids:
            result[user_id] = await self.is_online(user_id)

        return result

    # Typing Indicator Methods
    async def start_typing(self, user_id: str, chat_id: str) -> None:
        key = self._typing_key(user_id, chat_id)
        await self._redis.setex(key, self._typing_ttl_seconds, "1")

    async def stop_typing(self, user_id: str, chat_id: str) -> None:
        key = self._typing_key(user_id, chat_id)
        await self._redis.delete(key)

    async def get_typing_users(self, chat_id: str) -> list[str]:
        pattern = self._typing_pattern(chat_id)
        users = []

        async for key in self._redis.scan_iter(match=pattern, count=100):
            key_str = key.decode("utf-8") if isinstance(key, bytes) else key
            user_id = key_str.split(":")[-1]
            users.append(user_id)

        return users

    async def is_typing(self, user_id: str, chat_id: str) -> bool:
        key = self._typing_key(user_id, chat_id)
        exists = await self._redis.exists(key)
        return bool(exists)


# Keep old name for backward compatibility
RedisOnlineStatusService = RedisUserStatusService
