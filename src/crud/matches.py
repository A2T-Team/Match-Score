from sqlalchemy.orm import Session
from src.models.match import Match
from src.schemas.match import CreateMatchRequest, MatchUpdate


def create_match(db: Session, match_data: CreateMatchRequest) -> Match:
    new_match = Match(**match_data.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


def read_match_by_id(db: Session, match_id: str) -> Match:
    return db.query(Match).filter(Match.id == match_id).first()


def read_all_matches(db: Session):
    return db.query(Match).all()


def update_match(db: Session, match_id: str, updates: MatchUpdate) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if match:
        for key, value in updates.model_dump(exclude_unset=True).items():
            setattr(match, key, value)
        db.commit()
        db.refresh(match)
    return match


def delete_match(db: Session, match_id: str) -> bool:
    match = db.query(Match).filter(Match.id == match_id).first()
    if match:
        db.delete(match)
        db.commit()
        return True
    return False