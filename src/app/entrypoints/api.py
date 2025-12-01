from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.faststream import setup_dishka as fs_setup_dishka
from dishka.integrations.litestar import setup_dishka as ls_setup_dishka
from faststream.redis import RedisBroker
from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.logging.config import LoggingConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import (
    RedocRenderPlugin,
    ScalarRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
)
from litestar.openapi.spec import Components, SecurityScheme

from seedwork.application.event_bus import EventBus
from src.app.di import create_container
from src.app.entrypoints.ws import handler
from src.app.settings import get_settings
from src.core.chat.presentation.api import routes as chat_routes
from src.core.chat.presentation.events import routes as chat_handlers
from src.generic.iam.presentation.api import routes as iam_routes
from src.generic.iam.presentation.events import routes as iam_handlers


def configure_app() -> Litestar:
    cors_config = CORSConfig(
        allow_origins=[
            "*",
            # "http://localhost:5173",
            # "http://localhost:8128",
            # "https://grapegram-api.serveo.net",
            # "https://deploy-preview-8--dev-grapegram-web.netlify.app",
        ],
        allow_methods=["*"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True,
    )

    components = Components(
        security_schemes={
            "IAMTokenAuth": SecurityScheme(
                type="http",
                scheme="bearer",
                bearer_format="JWT",
            )
        }
    )
    openapi_config = OpenAPIConfig(
        title="Grapegram API",
        version="0.0.0",
        root_schema_site="swagger",
        render_plugins=[
            StoplightRenderPlugin(),
            ScalarRenderPlugin(),
            SwaggerRenderPlugin(),
            RedocRenderPlugin(
                js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
            ),
        ],
        security=[{"IAMTokenAuth": []}],
        components=components,
    )

    logging_config = LoggingConfig(
        root={"level": "INFO", "handlers": ["queue_listener"]},
        formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
        log_exceptions="always",
    )
    route_handlers = [*iam_routes, *chat_routes, handler]
    event_handlers = [*iam_handlers, *chat_handlers]

    channels_plugin = ChannelsPlugin(
        backend=MemoryChannelsBackend(history=200), arbitrary_channels_allowed=True
    )

    async_container = create_container(channels_plugin)

    @asynccontextmanager
    async def lifespan(app: Litestar):
        container = app.state.dishka_container
        redis_broker: RedisBroker = await container.get(RedisBroker)
        fs_setup_dishka(container=container, broker=redis_broker)

        event_bus: EventBus = await container.get(EventBus)
        event_bus.include_routes(event_handlers)
        await event_bus.start()

        yield
        await event_bus.stop()
        await container.close()

    app = Litestar(
        lifespan=[lifespan],
        route_handlers=[*route_handlers],
        on_app_init=[],
        cors_config=cors_config,
        openapi_config=openapi_config,
        logging_config=logging_config,
        plugins=[channels_plugin],
    )

    ls_setup_dishka(container=async_container, app=app)

    return app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "src.app.entrypoints.api:configure_app",
        host=settings.core.host,
        port=settings.core.port,
        reload=settings.core.debug,
        factory=True,
    )


if __name__ == "__main__":
    main()
