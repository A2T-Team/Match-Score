from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from src.schemas.match import CreateMatchRequest, MatchResponse, MatchUpdate
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from src.common.custom_responses import AlreadyExists, InternalServerError
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.crud import matches
import logging
import uuid
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(request: CreateMatchRequest, db: Session = Depends(get_db)):
    new_match = matches.create_match(db, request)
    return MatchResponse.model_validate(new_match)


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    match = matches.read_match_by_id(db, match_id)
    return MatchResponse.model_validate(match)


@router.get("/", response_model=list[MatchResponse])
def get_all_matches(
    tournament_id: uuid = None,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
):
    all_matches = matches.read_all_matches(db, tournament_id=tournament_id, sort_by_date=sort_by_date)
    return [MatchResponse.model_validate(match) for match in all_matches]


@router.put("/{match_id}", response_model=MatchResponse)
def update_match(match_id: uuid.UUID, updates: MatchUpdate, db: Session = Depends(get_db)):
    match = matches.update_match(db, match_id, updates)
    return MatchResponse.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    success = matches.delete_match(db, match_id)
    return success

@router.post("/match/{match_id}/update_stats", status_code=status.HTTP_200_OK)
def update_player_stats(match_id: int, db: Session = Depends(get_db)):
    result = matches.update_player_stats_after_match(db, match_id)
    return result