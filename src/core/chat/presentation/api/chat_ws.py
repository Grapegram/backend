from collections.abc import AsyncGenerator
from typing import Any

import anyio
from dishka import AsyncContainer
from dishka.integrations.litestar import FromDishka, inject_websocket
from litestar import WebSocket, websocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect
from litestar.handlers import send_websocket_stream

from src.core.chat.application.contracts.auth import AuthService


@websocket(
    "/ws/chat/{chat_id:str}",
)
@inject_websocket
async def live_chat(
    socket: WebSocket,
    channels: ChannelsPlugin,
    container: FromDishka[AsyncContainer],
    chat_id: str,
) -> None:
    async with container() as request_container:
        auth_service = await request_container.get(AuthService)
        await socket.accept()
        should_stop = anyio.Event()

        channel_name = f"chat-{chat_id}"
        is_authorized = False

        async def handle_stream() -> AsyncGenerator[str]:
            async with channels.start_subscription([channel_name]) as subscriber:
                async for message in subscriber.iter_events():
                    while not should_stop.is_set():
                        if is_authorized:
                            await socket.send_json(
                                {
                                    "channel": channel_name,
                                    "data": message
                                    if isinstance(message, dict)
                                    else {"message": message},
                                }
                            )
                        yield

        async def handle_receive() -> Any:
            nonlocal is_authorized
            async for message in socket.iter_json():
                action = message.get("action", "")

                if action == "authorize":
                    token = message.get("token")
                    if await auth_service.auth(token):
                        is_authorized = True
                        await socket.send_json({"status": "authorized"})
                    else:
                        is_authorized = False
                        await socket.send_json({"status": "unauthorized"})

        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(send_websocket_stream, socket, handle_stream())
                tg.start_soon(handle_receive)
        except WebSocketDisconnect:
            should_stop.set()
