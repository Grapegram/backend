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

from seedwork.application.event_bus import EventBus
from src.core.chat.application.contracts.auth import AuthService
from src.core.chat.application.events import (
    UserOffline,
    UserOnline,
)


@websocket(
    "/ws/chat-events/{user_id:str}",
)
@inject_websocket
async def chat_events(
    socket: WebSocket,
    channels: ChannelsPlugin,
    container: FromDishka[AsyncContainer],
    user_id: str,
) -> None:
    await socket.accept()
    should_stop = anyio.Event()

    is_authorized = False
    device_id = str(uuid4())
    chat_events = "chat-events"
    user_events = f"user-{user_id}"

    async def handle_stream() -> AsyncGenerator[str]:
        async with channels.start_subscription(
            [chat_events, user_events]
        ) as subscriber:
            while not should_stop.is_set():
                async for event in subscriber.iter_events():
                    if is_authorized:
                        await socket.send_text(event)
                yield

    async def handle_receive() -> Any:
        nonlocal is_authorized, user_id
        async for message in socket.iter_json():
            action = message.get("action", "")
            async with container() as request_container:
                event_bus = await request_container.get(EventBus)

                if action == "authorize":
                    token = message.get("token")
                    auth_service = await request_container.get(AuthService)
                    auth_user_id = await auth_service.auth(token)
                    if auth_user_id and auth_user_id == user_id:
                        is_authorized = True
                        await socket.send_json({"status": "authorized"})
                        await event_bus.publish(
                            UserOnline(user_id=user_id, device_id=device_id)
                        )
                    else:
                        is_authorized = False
                        await socket.send_json({"status": "unauthorized"})

                elif action == "ping" and is_authorized and user_id:
                    await event_bus.publish(
                        UserOnline(user_id=user_id, device_id=device_id)
                    )

    try:
        async with anyio.create_task_group() as tg:
            tg.start_soon(send_websocket_stream, socket, handle_stream())
            tg.start_soon(handle_receive)
    except WebSocketDisconnect:
        should_stop.set()
    except Exception as e:
        should_stop.set()
        raise e
    finally:
        if user_id:
            async with container() as request_container:
                event_bus = await request_container.get(EventBus)
                await event_bus.publish(
                    UserOffline(user_id=user_id, device_id=device_id)
                )
