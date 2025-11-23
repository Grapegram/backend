from typing import Protocol


class Notifier(Protocol):
    async def notify(self, channel: str, payload: dict) -> None: ...
