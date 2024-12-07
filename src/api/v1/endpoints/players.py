from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.player import CreatePlayerRequest, PlayerResponse #PlayerUpdate
from src.crud import players
import uuid
from src.core.auth import get_current_user
from src.models.user import User

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def post_player(request: CreatePlayerRequest, db: Session = Depends(get_db)):
    return players.create_player(db, request)
    #return PlayerResponse.model_validate(new_player)


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: uuid.UUID, db: Session = Depends(get_db)):
    return players.read_player_by_id(db, player_id)
    #return PlayerResponse.model_validate(player)


@router.get("/", response_model=list[PlayerResponse])
def get_all_players(db: Session = Depends(get_db), tournament_id: uuid.UUID | None = None):
    all_players = players.read_all_players(db, tournament_id)
    return [player for player in all_players]  #PlayerResponse.model_validate


# @router.put("/{player_id}", response_model=PlayerResponse)
# def update_player(player_id: uuid, updates: PlayerUpdate, db: Session = Depends(get_db)):
#     player = players.update_player(db, player_id, updates)
#     return PlayerResponse.model_validate(player)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: uuid.UUID, db: Session = Depends(get_db)):
    return players.delete_player(db, player_id)

@router.put("/connect/{player_id}", response_model=PlayerResponse)
def connect_user_to_player(player_id: uuid.UUID, user_id: uuid.UUID, db: Session = Depends(get_db)):
    return players.update_player_with_user(db, player_id, user_id)
    #return PlayerResponse.model_validate(player)

@router.get("/my_profile", response_model=PlayerResponse)
def get_user_player_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return players.read_current_user_player_profile(db, current_user)