from fastapi import APIRouter

from src.web.home import index_router


web_router = APIRouter()

web_router.include_router(index_router)
