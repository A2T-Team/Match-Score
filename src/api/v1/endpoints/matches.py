from src.api.deps import get_db
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.schemas.match import CreateMatchRequest, MatchResponse, MatchResult, MatchUpdateTime #MatchUpdate
from src.crud import matches
import uuid 
from src.models.user import User, Role
from src.core.auth import get_current_user
from src.common.custom_responses import (
    AlreadyExists,
    InternalServerError,
    NotFound,
    OK,
    Unauthorized,
    ForbiddenAccess,
    BadRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()
# matches_router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("/", status_code=status.HTTP_201_CREATED) #, response_model=MatchResponse
def post_match(request: CreateMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.create_match(db, request, current_user)
    #return MatchResponse.model_validate(new_match)


@router.get("/{match_id}") #, response_model=MatchResponse
def get_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    return matches.read_match_by_id(db, match_id)
    #return MatchResponse.model_validate(match)


@router.get("/")#, response_model=list[MatchResponse]
def get_all_matches(
    tournament_id: uuid.UUID = None,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
):
    all_matches = matches.read_all_matches(db, tournament_id=tournament_id, sort_by_date=sort_by_date)
    return [match for match in all_matches]

# @router.patch("/{match_id}", response_model=MatchResponse)
# def update_match(match_id: uuid.UUID, updates: MatchUpdate, db: Session = Depends(get_db)):
#     match = matches.update_match(db, match_id, updates)
#     return MatchResponse.model_validate(match)

@router.patch("/{match_id}/score") #, response_model=MatchResponse
def patch_match_score(match_id: uuid.UUID, updates: MatchResult, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_match_score(match_id, updates, db, current_user)
    #return MatchResponse.model_validate(match)

@router.patch("/{match_id}/date") #, response_model=MatchResponse
def patch_match_date(match_id: uuid.UUID, updates: MatchUpdateTime, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_match_date(db, match_id, updates, current_user)
    #return MatchResponse.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.delete_match(db, match_id, current_user)

@router.post("/match/{match_id}/update_stats", status_code=status.HTTP_200_OK)
def put_player_stats(match_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_player_stats_after_match(db, match_id, current_user)