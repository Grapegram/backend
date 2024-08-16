from fastapi import APIRouter, Request

from src.api.dependencies import SettingsDep

router = APIRouter()


@router.get("/")
async def index(
    request: Request,
    settings: SettingsDep,
) -> dict[str, str]:
    print(settings)
    return {"message": "Hello, Grapegram!"}
