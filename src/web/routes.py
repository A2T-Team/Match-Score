from fastapi import APIRouter

from src.web.home import index_router
from src.web.tournament import tournament_router
# from src.web.users import users_router
# from src.web.requests import requests_router

web_router = APIRouter()

web_router.include_router(index_router)
web_router.include_router(tournament_router)
# web_router.include_router(users_router)
# web_router.include_router(requests_router)

