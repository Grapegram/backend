from dataclasses import dataclass

from litestar.channels import ChannelsPlugin

from seedwork.application.notifier import Notifier


@dataclass
class LitestarNotifier(Notifier):
    channels: ChannelsPlugin

    async def notify(self, channel: str, payload: dict) -> None:
        self.channels.publish(payload, channels=[channel])
