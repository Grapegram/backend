import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core import get_settings

api_router = APIRouter()


@api_router.get("/")
def hello() -> dict:
    return {"message": "Hello, Grapegram!"}


def configure_app() -> FastAPI:
    setting = get_settings()
    app = FastAPI(
        title=setting.core.project_name,
        debug=setting.core.debug,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=setting.core.api_prefix)

    return app


def main() -> None:
    setting = get_settings()
    uvicorn.run(
        "main:configure_app",
        host=setting.core.host,
        port=setting.core.port,
        reload=setting.core.debug,
        factory=True,
    )


if __name__ == "__main__":
    main()
