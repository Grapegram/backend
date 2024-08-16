import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

api_router = APIRouter()


@api_router.get("/")
def hello() -> dict:
    return {"message": "Hello, Grapegram!"}


def configure_app() -> FastAPI:
    app = FastAPI(
        title="grapegram",
        openapi_url="/docs/openapi.json",
        debug=True,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api/v1")

    return app


def main() -> None:
    uvicorn.run(
        "main:configure_app",
        port=8000,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    main()
