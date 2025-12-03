from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import anyio
from dishka import AsyncContainer
from dishka.integrations.litestar import FromDishka, inject_websocket
from litestar import WebSocket, websocket
from litestar.channels import ChannelsPlugin
from litestar.exceptions import WebSocketDisconnect
from litestar.handlers import send_websocket_stream

from src.core.chat.application.contracts.auth import AuthService
from src.core.chat.application.contracts.user_status import UserStatusService


@websocket(
    "/ws/chat/",
)
@inject_websocket
async def live_chat(
    socket: WebSocket,
    channels: ChannelsPlugin,
    container: FromDishka[AsyncContainer],
) -> None:
    async with container() as request_container:
        auth_service = await request_container.get(AuthService)
        user_status_service = await request_container.get(UserStatusService)
        await socket.accept()
        should_stop = anyio.Event()

        channel_name = "chat-events"
        is_authorized = False
        user_id: str | None = None
        device_id = str(uuid4())

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
            nonlocal is_authorized, user_id
            async for message in socket.iter_json():
                action = message.get("action", "")

                if action == "authorize":
                    token = message.get("token")
                    auth_user_id = await auth_service.auth(token)
                    if auth_user_id:
                        is_authorized = True
                        user_id = auth_user_id
                        await user_status_service.mark_online(user_id, device_id)
                        await socket.send_json(
                            {"status": "authorized", "device_id": device_id}
                        )
                    else:
                        is_authorized = False
                        await socket.send_json({"status": "unauthorized"})

                elif action == "ping" and is_authorized and user_id:
                    await user_status_service.refresh_online(user_id, device_id)
                    await socket.send_json({"status": "pong"})

                elif action == "start_typing" and is_authorized and user_id:
                    chat_id = message.get("chat_id")
                    if chat_id:
                        await user_status_service.start_typing(user_id, chat_id)
                        await channels.publish(
                            {
                                "type": "typing_started",
                                "user_id": user_id,
                                "chat_id": chat_id,
                            },
                            channel_name,
                        )

                elif action == "stop_typing" and is_authorized and user_id:
                    chat_id = message.get("chat_id")
                    if chat_id:
                        await user_status_service.stop_typing(user_id, chat_id)
                        await channels.publish(
                            {
                                "type": "typing_stopped",
                                "user_id": user_id,
                                "chat_id": chat_id,
                            },
                            channel_name,
                        )

        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(send_websocket_stream, socket, handle_stream())
                tg.start_soon(handle_receive)
        except WebSocketDisconnect:
            should_stop.set()
        finally:
            if user_id:
                await user_status_service.mark_offline(user_id, device_id)
