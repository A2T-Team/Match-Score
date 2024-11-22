from sqlalchemy.orm import Session
from src.models.match import Match
from src.models.player import Player

from fastapi import HTTPException, status
from src.schemas.match import CreateMatchRequest, MatchUpdate


def create_match(db: Session, match_data: CreateMatchRequest) -> Match:
    new_match = Match(**match_data.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


def read_match_by_id(db: Session, match_id: str) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


def read_all_matches(db: Session):
    matches = db.query(Match).all()
    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Matches")
    return matches


def update_match(db: Session, match_id: str, updates: MatchUpdate) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if match:
        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(match, key, value)
        db.commit()
        db.refresh(match)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


def delete_match(db: Session, match_id: str) -> bool:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    db.delete(match)
    db.commit()
    return True

def update_player_stats_after_match(db: Session, match_id: int):
    match = db.query(Match).filter_by(id=match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )

    # Assuming match result contains these fields: player_id, result (win, loss, draw)
    player_1 = db.query(Player).filter_by(id=match.player_a).first()
    if not player_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="First player not found"
        )
    player_2 = db.query(Player).filter_by(id=match.player_b).first()
    if not player_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Second player not found"
        )
    player_1.matches_played += 1
    player_2.matches_played += 1
    if match.result_code == 'player 1':
        player_1.wins += 1
        player_2.losses += 1
    elif match.result_code == 'player 2':
        player_1.losses += 1
        player_2.wins += 1
    else:
        player_1.draws += 1
        player_2.draws += 1
        db.commit()
        db.refresh(player_1, player_2)
    
    return {"detail": "Player statistics updated successfully"}