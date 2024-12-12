from src.api.deps import get_db
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.schemas.match import CreateMatchRequest, MatchResult, MatchUpdateTime
from src.crud import matches
from uuid import UUID
from src.models.user import User, Role
from src.core.auth import get_current_user
from src.common.custom_responses import (
    Unauthorized,
    ForbiddenAccess
)

logger = logging.getLogger(__name__)

router = APIRouter()



@router.post("/", status_code=status.HTTP_201_CREATED)
def post_match(request: CreateMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.create_match(db, request, current_user)



@router.get("/matches")
def get_all_matches(
    tournament_id: UUID = None,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
):
    all_matches = matches.read_all_matches(db, tournament_id=tournament_id, sort_by_date=sort_by_date)
    return [match for match in all_matches]

@router.get("/{match_id}")
def get_match(match_id: UUID, db: Session = Depends(get_db)):
    return matches.read_match_by_id(db, match_id)



@router.patch("/{match_id}/score")
def patch_match_score(match_id: UUID, updates: MatchResult, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_match_score(match_id, updates, db, current_user)

@router.patch("/{match_id}/date")
def patch_match_date(match_id: UUID, updates: MatchUpdateTime, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_match_date(db, match_id, updates, current_user)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.delete_match(db, match_id, current_user)

@router.put("/match/{match_id}/update_stats", status_code=status.HTTP_200_OK)
def put_player_stats(match_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user is None:
        return Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        return ForbiddenAccess()
    return matches.update_player_stats_after_match(db, match_id, current_user)