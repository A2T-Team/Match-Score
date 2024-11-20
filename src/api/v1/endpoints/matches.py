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


matches_router = APIRouter(prefix="/matches", tags=["Matches"])


@matches_router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(request: CreateMatchRequest, db: Session = Depends(get_db)):
    new_match = matches.create_match(db, request)
    return MatchResponse.model_validate(new_match)


@matches_router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    match = matches.read_match_by_id(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return MatchResponse.model_validate(match)


@matches_router.get("/", response_model=list[MatchResponse])
def get_all_matches(db: Session = Depends(get_db)):
    matches = matches.read_all_matches(db)
    return [MatchResponse.model_validate(match) for match in matches]


@matches_router.patch("/{match_id}", response_model=MatchResponse)
def update_match(match_id: uuid.UUID, updates: MatchUpdate, db: Session = Depends(get_db)):
    match = matches.update_match(db, match_id, updates)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return MatchResponse.model_validate(match)


@matches_router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    success = matches.delete_match(db, match_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
