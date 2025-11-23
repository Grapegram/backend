import json

from litestar import WebSocket, websocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect


@websocket("/ws")
async def handler(socket: WebSocket, channels: ChannelsPlugin) -> None:
    await socket.accept()

    try:
        async with channels.start_subscription(["events"]) as subscriber:
            await channels.put_subscriber_history(subscriber, ["events"])

            async for message in subscriber.iter_events():
                await socket.send_json(
                    {
                        "channel": "events",
                        "data": json.loads(message),
                    }
                )
    except WebSocketDisconnect:
        pass
