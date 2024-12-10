from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.schemas.player import CreatePlayerRequest, PlayerResponse, ParticipantResponse, PlayerUpdate
from src.crud import players
from uuid import UUID
from src.core.auth import get_current_user
from src.models.user import User, Role
from src.common.custom_responses import (
    AlreadyExists,
    InternalServerError,
    NotFound,
    OK,
    Unauthorized,
    ForbiddenAccess,
    BadRequest,
)

router = APIRouter()


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def create_player(request: CreatePlayerRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return players.create_player(db, request)

@router.get("/my_profile", response_model=PlayerResponse)
def get_user_player_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")
    if current_user.role != Role.USER:
        return ForbiddenAccess()
    return players.read_current_user_player_profile(db, current_user)

@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: UUID, db: Session = Depends(get_db)):
    return players.read_player_by_id(db, player_id)


@router.get("/", response_model=list[PlayerResponse])
def get_all_players(db: Session = Depends(get_db), tournament_id: UUID | None = None):
    all_players = players.read_all_players(db, tournament_id)
    return [player for player in all_players]  #PlayerResponse.model_validate


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: UUID, player_data: PlayerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")
    return players.update_player(db, player_id, player_data, current_user)


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return players.delete_player(db, player_id, current_user)

@router.put("/connect/{player_id}", response_model=PlayerResponse)
def connect_user_to_player(player_id: UUID, user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.USER}:
        return ForbiddenAccess()
    return players.update_player_with_user(db, player_id, user_id)

@router.get("/{player_id}/{tournament_id}", response_model=ParticipantResponse)
def get_player_in_tournament(player_id: UUID, tournament_id: UUID, db: Session = Depends(get_db)):
    return players.read_player_by_id_and_tournament(db, player_id, tournament_id)
