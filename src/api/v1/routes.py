from fastapi import APIRouter

from src.api.v1.endpoints import items
from src.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
