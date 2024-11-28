from fastapi import APIRouter

from src.api.v1.endpoints import items
from src.api.v1.endpoints import users
from src.api.v1.endpoints import requests
from src.api.v1.endpoints import tournaments
from src.api.v1.endpoints import players
from src.api.v1.endpoints import matches


api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(requests.router, prefix="/requests", tags=["Requests"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])
api_router.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(players.router, prefix="/players", tags=["Players"])
