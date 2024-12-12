from sqlalchemy.orm import Session
from src.models.match import Match, MatchFormat, ResultCodes
from src.models.player import Player
from src.models.user import User
from src.models.tournament import Tournament, TournamentParticipants
from src.crud.tournaments import get_tournament
from datetime import timedelta
from uuid import UUID
from fastapi import HTTPException, status
from src.schemas.match import CreateMatchRequest, MatchUpdateTime, MatchResult

def match_format_to_id(value: str, db_session: Session):
    """
    Retrieves the ID of the match format based on the format type.

    Args:
        value (str): The type of the match format.
        db_session (Session): The database session.

    Returns:
        int: The ID of the match format.
    """
    format = db_session.query(MatchFormat).filter(MatchFormat.type == value).first()
    if format is None:
        return None

    return format.id

def match_result_to_id(value: str, db_session: Session):
    """
    Retrieves the ID of the result code based on the result description.

    Args:
        value (str): The result description.
        db_session (Session): The database session.

    Returns:
        int: The ID of the result code.
    """
    result = db_session.query(ResultCodes).filter(ResultCodes.result == value).first()
    return result.id

def create_match(db: Session, match_data: CreateMatchRequest, current_user: User) -> Match:
    """
    Creates a new match.

    Args:
        db (Session): The database session.
        match_data (CreateMatchRequest): The data required to create a new match.
        current_user (User): The current authenticated user.

    Returns:
        Match: The newly created match.
    """
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
            author_id = current_user.id,
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
            author_id = current_user.id,
        )

    #new_match = Match(**match_data.model_dump())
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


def read_match_by_id(db: Session, match_id: UUID) -> Match:
    """
    Retrieves a match by its ID.

    Args:
        db (Session): The database session.
        match_id (UUID): The unique identifier of the match.

    Returns:
        Match: The match corresponding to the provided ID.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


def read_all_matches(db: Session, tournament_id: UUID = None, sort_by_date: bool = False):
    """
    Retrieves all matches, optionally filtered by tournament ID or sorted by date.

    Args:
        db (Session): The database session.
        tournament_id (UUID, optional): The ID of the tournament to filter matches. Defaults to None.
        sort_by_date (bool, optional): Whether to sort matches by start date. Defaults to False.

    Returns:
        list: A list of all matches matching the criteria.
    """
    query = db.query(Match)

    if tournament_id is not None:
        query = query.filter(Match.tournament_id == tournament_id)

    if sort_by_date:
        query = query.order_by(Match.start_time)

    matches = query.all()

    if not matches:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Matches")
    
    return matches



def check_score_limit(end_condition, score_a, score_b):
    """
    Validates that the match score does not exceed the end condition.

    Args:
        end_condition (int): The end condition for the match.
        score_a (int): The score of player A.
        score_b (int): The score of player B.

    Raises:
        HTTPException: If the score does not adhere to the end condition.
    """
    if end_condition is None:
        raise ValueError("End condition cannot be None.")
    if score_a is None or score_b is None:
        raise ValueError("Scores cannot be None.")

    if score_a > end_condition or score_b > end_condition or (score_a == end_condition and score_b == end_condition) or (score_a != end_condition and score_b != end_condition):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One and only one score must be as the end condition")

def update_match_score(match_id: UUID, updates: MatchResult, db: Session, current_user: User):
    """
    Updates the score of a match.

    Args:
        match_id (UUID): The unique identifier of the match.
        updates (MatchResult): The updated match result data.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Match: The updated match.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    if match.author_id != current_user.id and current_user.role !='ADMIN':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't update this match")
    if (updates.score_a > updates.score_b and (updates.result_code == 'player 2' or updates.result_code == 'draw')) or (updates.score_a < updates.score_b and (updates.result_code == 'player 1' or updates.result_code == 'draw')) or (updates.score_a == updates.score_b and (updates.result_code == 'player 1' or updates.result_code == 'player 2')):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid result")
    if match.format_id == 1:
        check_score_limit(match.end_condition, updates.score_a, updates.score_b)

        
    match.score_a = updates.score_a
    match.score_b = updates.score_b
    result_id = match_result_to_id(updates.result_code, db)
    match.result_code = result_id
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return match

def update_match_date(db: Session, match_id: UUID, updates: MatchUpdateTime, current_user: User):
    """
    Updates the datetime of a match.

    Args:
        match_id (UUID): The unique identifier of the match.
        updates (MatchResult): The updated match result data.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Match: The updated match.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    if match.author_id != current_user.id and current_user.role !='ADMIN':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't update this match")
    if match.start_time > updates.start_time:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Start time can't be before the original time")
    
    if match.format_id == 0:
        match.start_time = updates.start_time
        match.end_time = updates.start_time + timedelta(minutes=match.end_condition)
    else:
        match.start_time = updates.start_time
        match.end_time = updates.end_time
    
    db.add(match)
    db.commit()
    db.refresh(match)
    
    return match


def delete_match(db: Session, match_id: UUID, current_user: User) -> bool:
    """
    Deletes a match by its ID.

    Args:
        db (Session): The database session.
        match_id (UUID): The unique identifier of the match.
        current_user (User): The current authenticated user.

    Returns:
        bool: True if the match was successfully deleted.
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    if match.author_id != current_user.id and current_user.role !='ADMIN':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't delete this match")
    db.delete(match)
    db.commit()
    return True

def update_player_stats_after_match(db: Session, match_id: UUID, current_user: User):
    """
    Updates the players statistics after match.

    Args:
        match_id (UUID): The unique identifier of the match.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Message for succsessfuly updated stats
    """
    match = db.query(Match).filter_by(id=match_id).first()

    if  match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Match not found"
        )
    
    if match.author_id != current_user.id and current_user.role !='ADMIN':
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't update this match")

    player_1 = db.query(Player).filter_by(id=match.player_a_id).first()

    if not player_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="First player not found"
        )
    
    player_2 = db.query(Player).filter_by(id=match.player_b_id).first()

    if not player_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Second player not found"
        )
    
    player_1.matches_played += 1
    player_2.matches_played += 1 

    if match.tournament_id:
        tournament = db.query(Tournament).filter_by(id=match.tournament_id).first()
        participant_1 = db.query(TournamentParticipants).filter_by(tournament_id=match.tournament_id , player_id=player_1.id).first()
        participant_2 = db.query(TournamentParticipants).filter_by(tournament_id=match.tournament_id , player_id=player_2.id).first()
        next_match = db.query(Match).filter_by(serial_number = match.serial_number // 2).first()

        if tournament.format_id == 1:

            if match.result_code == 1:
                player_1.wins += 1
                player_2.losses += 1
                participant_1.score += tournament.win_points
                participant_1.stage += 1

            elif match.result_code == 2:
                player_1.losses += 1
                player_2.wins += 1
                participant_2.score += tournament.win_points
                participant_2.stage += 1

            else:
                player_1.draws += 1
                player_2.draws += 1
                participant_1.score += tournament.draw_points
                participant_2.score += tournament.draw_points

        else:
            if match.result_code == 1:
                player_1.wins += 1
                player_2.losses += 1
                participant_1.stage += 1
                if not next_match.player_a:
                    next_match.player_a = player_1.id
                else:
                    next_match.player_b = player_1.id

            elif match.result_code == 2:
                player_1.losses += 1
                player_2.wins += 1
                participant_2.stage += 1
                if not next_match.player_a:
                    next_match.player_a = player_2.id
                else:
                    next_match.player_b = player_2.id

            else:
                player_1.draws += 1
                player_2.draws += 1
    
    else:
        if match.result_code == 1:
            player_1.wins += 1
            player_2.losses += 1

        elif match.result_code == 2:
            player_1.losses += 1
            player_2.wins += 1

        else:
            player_1.draws += 1
            player_2.draws += 1

    db.commit()
    for player in [player_1, player_2]:
        db.refresh(player)
    
    return {"detail": "Player statistics updated successfully"}