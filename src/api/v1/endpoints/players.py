from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.player import CreatePlayerRequest, PlayerResponse, PlayerUpdate
from src.crud import players

players_router = APIRouter(prefix="/players", tags=["Players"])


@players_router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(request: CreatePlayerRequest, db: Session = Depends(get_db)):
    new_player = players.create_player(db, request)
    return PlayerResponse.model_validate(new_player)


@players_router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = players.get_player_by_id(db, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return PlayerResponse.model_validate(player)


@players_router.get("/", response_model=list[PlayerResponse])
def get_all_players(db: Session = Depends(get_db)):
    players = players.get_all_players(db)
    return [PlayerResponse.model_validate(player) for player in players]


@players_router.patch("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, updates: PlayerUpdate, db: Session = Depends(get_db)):
    player = players.update_player(db, player_id, updates)
    return PlayerResponse.model_validate(player)


@players_router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    success = players.delete_player(db, player_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )