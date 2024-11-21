from src.schemas.tournament import CreateTournamentRequest
from src.models.tournament import Tournament
from src.models.match import Match
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from src.common.custom_responses import AlreadyExists
from uuid import UUID
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
        current_user_id (UUID): The ID of the user creating the category.

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
    count = db.query(Tournament).filter(Tournament.name == tournament_name).count()
    return count > 0


def get_tournament(
    db_session: Session,
    tournament_id: UUID,
) -> Tournament | None:  # current_user: User = Depends(get_current_user))
    """
    Retrieve a tournament by its ID from the database.

    Parameters:
        db_session (Session): The database session to use for the query.
        tournament_id (UUID): The ID of the tournament to retrieve.

    Returns:
        Tournament | None: The tournament object if found, or None if no tournament exists with the given ID.
    """

    tournament = (
        db_session.query(Tournament).filter(Tournament.id == tournament_id).first()
    )
    if tournament is None:
        return None

    return tournament


def get_matches_in_tournament(db_session: Session, tournament_id: UUID) -> list[Match]:
    """
    Retrieve all matches associated with a specific tournament.

    Parameters:
        db_session (Session): The database session to use for the query.
        tournament_id (UUID): The ID of the tournament whose matches are to be retrieved.

    Returns:
        list[Match]: A list of Match objects associated with the specified tournament.
                     Returns an empty list if no matches are found.
    """

    matches = db_session.query(Match).filter(Match.tournament_id == tournament_id).all()
    if not matches:
        return []

    return matches


def view_all_tournaments(
    db_session: Session,
    skip: int = 0,
    limit: int = 100,
    sort: str = None,
    search: str = None,
):  # ccurrent_user: User = Depends(get_current_user)
    
    tournaments = db_session.query(Tournament)

    if search:
        tournaments = tournaments.filter(Tournament.name.contains(search))
    if sort:
        if sort.lower() == "desc":
            tournaments = tournaments.order_by(desc(Tournament.id))
        elif sort.lower() == "asc":
            tournaments = tournaments.order_by(asc(Tournament.id))
    tournaments = tournaments.offset(skip).limit(limit).all()

    return tournaments
