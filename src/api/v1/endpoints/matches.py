from src.api.deps import get_db
import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.schemas.match import CreateMatchRequest, MatchResponse, MatchResult, MatchUpdateTime #MatchUpdate
from src.crud import matches
import uuid 

logger = logging.getLogger(__name__)

router = APIRouter()
# matches_router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def post_match(request: CreateMatchRequest, db: Session = Depends(get_db)):
    new_match = matches.create_match(db, request)
    return MatchResponse.model_validate(new_match)


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    match = matches.read_match_by_id(db, match_id)
    return MatchResponse.model_validate(match)


@router.get("/", response_model=list[MatchResponse])
def get_all_matches(
    tournament_id: uuid.UUID = None,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
):
    all_matches = matches.read_all_matches(db, tournament_id=tournament_id, sort_by_date=sort_by_date)
    return [MatchResponse.model_validate(match) for match in all_matches]

# @router.patch("/{match_id}", response_model=MatchResponse)
# def update_match(match_id: uuid.UUID, updates: MatchUpdate, db: Session = Depends(get_db)):
#     match = matches.update_match(db, match_id, updates)
#     return MatchResponse.model_validate(match)

@router.put("/{match_id}", response_model=MatchResponse)
def put_match_score(match_id: uuid.UUID, updates: MatchResult, db: Session = Depends(get_db)):
    match = matches.update_match_score(db, match_id, updates)
    return MatchResponse.model_validate(match)

@router.put("/{match_id}", response_model=MatchResponse)
def put_match_score(match_id: uuid.UUID, updates: MatchUpdateTime, db: Session = Depends(get_db)):
    match = matches.update_match_date(db, match_id, updates)
    return MatchResponse.model_validate(match)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(match_id: uuid.UUID, db: Session = Depends(get_db)):
    success = matches.delete_match(db, match_id)
    return success

@router.post("/match/{match_id}/update_stats", status_code=status.HTTP_200_OK)
def put_player_stats(match_id: uuid.UUID, db: Session = Depends(get_db)):
    result = matches.update_player_stats_after_match(db, match_id)
    return result