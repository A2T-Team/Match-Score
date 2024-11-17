from src.schemas.tournament import CreateTournamentRequest
from src.models.tournament import Tournament
from sqlalchemy.orm import Session
from src.common.custom_responses import AlreadyExists
import logging

logger = logging.getLogger(__name__)


def tournament_format_to_id(value):
    return 1 if value == "league" else 0


def match_format_to_id(value):
    return 1 if value == "score" else 0


def create(
    tournament: CreateTournamentRequest,
    db_session: Session,  # current_user_id: int
):
    """
    Create a new tournament in the database, using the provided CreateTournamentRequest object
    and the current user ID.

    Parameters:
        tournament (CreateTournamentRequest): An instance of the `CreateTournamentRequest` class.
        current_user_id (int): The ID of the user creating the category.

    Returns:
        Tournament: An instance of the `Tournament` class with all attributes of the newly created tournament.
    """

    # check_admin_role(current_user)
    
    # if tournament_name_exists(db=db_session, tournament_name=tournament.name):
    #     raise AlreadyExists(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="The tournament name is not available."
    #     ) 

    db_tournament = Tournament(
        name=tournament.name,
        format_id=tournament_format_to_id(tournament.format),
        match_format_id=match_format_to_id(tournament.match_format),
        start_time=tournament.start_time,
        end_time=tournament.end_time,
        prize=tournament.prize,
        win_points=tournament.win_points,
        draw_points=tournament.draw_points,
        author_id=tournament.author_id,
    )
    db_session.add(db_tournament)
    db_session.commit()
    db_session.refresh(db_tournament)

    return db_tournament


def tournament_name_exists(db: Session, tournament_name: str) -> bool:
    """
    Check if a tournament with the given name exists in the database.

    Parameters:
        db (Session): The database session to use for the query.
        tournament_name (str): The name of the tournament to check.

    Returns:
        bool: True if a tournament with the specified name exists, False otherwise.
    """
    count = (
        db.query(Tournament)
        .filter(Tournament.name == tournament_name)
        .count()
    )
    return count > 0