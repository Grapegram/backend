from fastapi import APIRouter

from .routes import test

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["test"])

__all__ = ["api_router"]
