from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.litestar import DishkaRouter, setup_dishka
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.logging.config import LoggingConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin, StoplightRenderPlugin

from src.app.di import create_container
from src.app.settings import get_settings
from src.generic.iam.presentation.api import routes as iam_routes


def configure_app() -> Litestar:
    cors_config = CORSConfig(
        allow_origins=[
            "http://localhost:5174",
            "http://localhost:8128",
            "https://grapegram-api.serveo.net",
            "https://deploy-preview-8--dev-grapegram-web.netlify.app",
        ],
        allow_methods=["*"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True,
    )

    openapi_config = OpenAPIConfig(
        title="Grapegram API",
        version="0.0.0",
        render_plugins=[
            RedocRenderPlugin(
                js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
            )
        ],
    )

    logging_config = LoggingConfig(
        root={"level": "INFO", "handlers": ["queue_listener"]},
        formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
        log_exceptions="always",
    )
    route_handlers = [*iam_routes]
    router = DishkaRouter("", route_handlers=route_handlers)

    @asynccontextmanager
    async def lifespan(app: Litestar):
        yield
        await app.state.dishka_container.close()

    app = Litestar(
        lifespan=[lifespan],
        route_handlers=[router],
        on_app_init=[],
        cors_config=cors_config,
        openapi_config=openapi_config,
        logging_config=logging_config,
    )
    setup_dishka(container=create_container(), app=app)
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
