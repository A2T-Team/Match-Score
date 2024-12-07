from fastapi import APIRouter

from src.web.home import index_router
from src.web.tournament import tournament_router


web_router = APIRouter()

web_router.include_router(index_router)
web_router.include_router(tournament_router)
