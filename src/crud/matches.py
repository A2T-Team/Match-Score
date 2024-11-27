from sqlalchemy.orm import Session
from src.models.match import Match, MatchFormat
from src.models.player import Player
from src.models.tournament import Tournament, TournamentParticipants
from src.common.custom_exceptions import NotFound, ScoreLimit
from src.crud.tournaments import get_tournament
from datetime import timedelta
import uuid
from fastapi import HTTPException, status
from src.schemas.match import CreateMatchRequest, MatchUpdateTime, MatchResult #MatchUpdate

def match_format_to_id(value: str, db_session: Session):
    format = db_session.query(MatchFormat).filter(MatchFormat.type == value).first()
    if format is None:
        return None

    return format.id


def create_match(db: Session, match_data: CreateMatchRequest) -> Match:
    if match_data.tournament_id:
        tournament = get_tournament(db, match_data.tournament_id)
        if not tournament:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")
        new_match = Match(
            format_id = tournament.match_format_id,
            end_condition = match_data.end_condition,
            player_a_id = match_data.player_a,
            player_b_id = match_data.player_b,
            start_time = match_data.start_time,
            end_time = match_data.end_time,
            prize = 0,
            author_id = match_data.author_id,
            tournament_id = match_data.tournament_id,
            stage = match_data.stage,
            serial_number = match_data.serial_number
        )
    else:
        match_format_id = match_format_to_id(match_data.format, db)
        new_match = Match(
            format_id = match_format_id,
            end_condition = match_data.end_condition,
            player_a_id = match_data.player_a,
            player_b_id = match_data.player_b,
            start_time = match_data.start_time,
            end_time = match_data.end_time,
            prize = match_data.prize,
            author_id = match_data.author_id,
        )

    #new_match = Match(**match_data.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


    format_id = Column(Integer, ForeignKey("match_format.id"), nullable = False)
    end_condition = Column(Integer, nullable=False)
    player_a_id = Column(UUID, ForeignKey("players.id"))
    player_b_id = Column(UUID, ForeignKey("players.id"))
    score_a = Column(Integer)
    score_b = Column(Integer)
    result_code = Column(Integer, ForeignKey("result_codes.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    prize = Column(Integer)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(UUID, ForeignKey("tournaments.id"))
    stage = Column(Integer)
    serial_number = Column(Integer)



def read_match_by_id(db: Session, match_id: uuid.UUID) -> Match:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


def read_all_matches(db: Session, tournament_id: uuid.UUID = None, sort_by_date: bool = False):
    query = db.query(Match)

    if tournament_id is not None:
        query = query.filter(Match.tournament_id == tournament_id)

    if sort_by_date:
        query = query.order_by(Match.start_time)

    matches = query.all()

    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Matches")
    
    return matches


# def update_match(db: Session, match_id: uuid, updates: MatchUpdate) -> Match:
#     match = db.query(Match).filter(Match.id == match_id).first()
#     if match:
#         for key, value in updates.model_dump(exclude_unset=True).items():
#             setattr(match, key, value)
#         db.commit()
#         db.refresh(match)
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
#     return match

def update_match_score(db: Session, match_id: uuid, updates: MatchResult):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    if match.format_id == 1: # trqbwa da proverq chisloto
        if (
            updates.score_a > match.end_condition or updates.score_b > match.end_condition or
            (updates.score_a == match.end_condition and updates.score_b == match.end_condition) or
            (updates.score_a != match.end_condition and updates.score_b != match.end_condition)
        ):            
            raise ScoreLimit(match.end_condition)
        
    match.score_a = updates.score_a
    match.score_b = updates.score_b
    match.result_code = updates.result_code
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return match

def update_match_date(db: Session, match_id: uuid, updates: MatchUpdateTime):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    
    if match.format_id == 2: # trqbwa da proverq chisloto
        match.start_time = updates.start_time
        match.end_time = updates.start_time + timedelta(minutes=match.end_condition)
    else:
        match.start_time = updates.start_time
        match.end_time = updates.end_time
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return match


def delete_match(db: Session, match_id: uuid.UUID) -> bool:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    db.delete(match)
    db.commit()
    return True

def update_player_stats_after_match(db: Session, match_id: uuid.UUID):
    match = db.query(Match).filter_by(id=match_id).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    
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

    if match.tournament_id:
        tournament = db.query(Tournament).filter_by(id=match.tournament_id).first()
        
        # Stage moving forward when there is tournament_id
        # points at end of tournament?

        if tournament.format_id == 1:
            participant_1 = db.query(TournamentParticipants).filter_by(tournament_id=match.tournament_id , player_id=player_1.id).first()
            participant_2 = db.query(TournamentParticipants).filter_by(tournament_id=match.tournament_id , player_id=player_2.id).first()

            if match.result_code == 'player 1':
                player_1.wins += 1
                player_2.losses += 1
                #player_1.points += tournament.win_points
                participant_1.score += tournament.win_points

            elif match.result_code == 'player 2':
                player_1.losses += 1
                player_2.wins += 1
                #player_2.points += tournament.win_points
                participant_2.score += tournament.win_points

            else:
                player_1.draws += 1
                player_2.draws += 1
                #player_2.points += tournament.draw_points
                #player_2.points += tournament.draw_points
                participant_1.score += tournament.draw_points
                participant_2.score += tournament.draw_points

        else:
            if match.result_code == 'player 1':
                player_1.wins += 1
                player_2.losses += 1

            elif match.result_code == 'player 2':
                player_1.losses += 1
                player_2.wins += 1

            else:
                player_1.draws += 1
                player_2.draws += 1
    
    else:
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