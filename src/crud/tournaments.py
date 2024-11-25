from src.schemas.tournament import TournamentSchema, Participant, UpdateTournamentDates
from src.models.tournament import Tournament, TournamentFormat, TournamentParticipants
from src.models.match import Match, MatchFormat
from src.models.player import Player
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, and_
from src.common.custom_responses import AlreadyExists
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from src.common.custom_exceptions import NotFound, InvalidNumberOfPlayers
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def tournament_format_to_id(value: str, db_session: Session):
    format = (
        db_session.query(TournamentFormat)
        .filter(TournamentFormat.type == value)
        .first()
    )
    if format is None:
        return None

    return format.id


def match_format_to_id(value: str, db_session: Session):
    format = db_session.query(MatchFormat).filter(MatchFormat.type == value).first()
    if format is None:
        return None

    return format.id


def create(
    tournament: TournamentSchema,
    db_session: Session,  # current_user_id: int
):
    """
    Create a new tournament in the database, using the provided TournamentSchema object
    and the current user ID.

    Parameters:
        tournament (TournamentSchema): An instance of the `TournamentSchema` class.
        current_user_id (UUID): The ID of the user creating the category.

    Returns:
        Tournament: An instance of the `Tournament` class with all attributes of the newly created tournament.
    """

    # check_admin_role(current_user)

    # if tournament_name_exists(db=db_session, tournament_name=tournament.name):
    #     raise AlreadyExists(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="The tournament name is not available."
    #     )
    format_id = tournament_format_to_id(tournament.format, db_session)
    if format_id is None:
        raise NotFound(key="format", key_value=tournament.format)

    match_format_id = match_format_to_id(tournament.match_format, db_session)
    if match_format_id is None:
        raise NotFound(key="match_format", key_value=tournament.match_format)

    db_tournament = Tournament(
        name=tournament.name,
        format_id=format_id,
        match_format_id=match_format_id,
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
) -> Tournament | None:  # TODO current_user: User = Depends(get_current_user))
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

    return tournament


# def get_matches_in_tournament(db_session: Session, tournament_id: UUID) -> list[Match]:
#     """
#     Retrieve all matches associated with a specific tournament.

#     Parameters:
#         db_session (Session): The database session to use for the query.
#         tournament_id (UUID): The ID of the tournament whose matches are to be retrieved.

#     Returns:
#         list[Match]: A list of Match objects associated with the specified tournament.
#                      Returns an empty list if no matches are found.
#     """

#     matches = db_session.query(Match).filter(Match.tournament_id == tournament_id).all()
#     if not matches:
#         return []

#     return matches


def view_all_tournaments(
    db_session: Session,
    offset: int = 0,
    limit: int = 100,
    sort: str = None,
    search: str = None,
):  # TODO ccurrent_user: User = Depends(get_current_user)

    tournaments = db_session.query(Tournament)

    if search:
        tournaments = tournaments.filter(Tournament.name.ilike(f"%{search}%"))
    if sort:
        if sort.lower() == "desc":
            tournaments = tournaments.order_by(desc(Tournament.start_time))
        elif sort.lower() == "asc":
            tournaments = tournaments.order_by(asc(Tournament.start_time))
    tournaments = tournaments.offset(offset).limit(limit).all()

    return tournaments


def get_participant(
    db_session: Session, participant: Participant
) -> Participant | None:
    db_participant = (
        db_session.query(Player)
        .filter(
            and_(
                Player.first_name.ilike(participant.first_name),
                Player.last_name.ilike(participant.last_name),
            )
        )
        .first()
    )
    return db_participant


def create_player(db_session: Session, participant: Participant):
    new_profile = Player(
        first_name=participant.first_name, last_name=participant.last_name
    )
    db_session.add(new_profile)
    db_session.commit()
    db_session.refresh(new_profile)

    return new_profile


def add_participants(
    db_session: Session, tournament_id: UUID, participants: list[Participant]
):  # TODO ccurrent_user: User = Depends(get_current_user)

    result = {}

    for participant in participants:
        db_player = get_participant(db_session, participant)
        if db_player is None:
            db_player = create_player(db_session, participant)
        tournament_participant = TournamentParticipants(
            tournament_id=tournament_id,
            player_id=db_player.id,
        )
        result[db_player.id] = {
            "first_name": db_player.first_name,
            "last_name": db_player.last_name,
        }
        db_session.add(tournament_participant)
        try:
            db_session.commit()
            result[db_player.id]["status"] = "Added"
        except IntegrityError:
            db_session.rollback()
            result[db_player.id]["status"] = "Already exists"

    return result


def get_tournament_participant(
    db_session: Session,
    participant: Participant,
    tournament_id: UUID,
) -> TournamentParticipants | None:
    db_player = get_participant(db_session, participant)
    if db_player is None:
        return None

    tournament_particiopant = (
        db_session.query(TournamentParticipants)
        .filter(
            and_(
                TournamentParticipants.player_id == db_player.id,
                TournamentParticipants.tournament_id == tournament_id,
            )
        )
        .first()
    )
    return tournament_particiopant


def delete_players(
    db_session: Session, tournament_id: UUID, participants: list[Participant]
):  # TODO ccurrent_user: User = Depends(get_current_user)
    result = {}

    for participant in participants:
        full_name = f"{participant.first_name} {participant.last_name}"
        result[full_name] = {}
        tournament_participant = get_tournament_participant(
            db_session, participant, tournament_id
        )
        if tournament_participant is None:
            result[full_name]["status"] = "Not Found"
            continue

        db_session.delete(tournament_participant)
        db_session.commit()
        result[full_name]["status"] = "Deleted"

    return result


def update_dates(
    tournament_id: UUID, dates: UpdateTournamentDates, db_session: Session
):
    # TODO current_user: User = Depends(get_current_user)
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)

    tournament.start_time = dates.start_time
    tournament.end_time = dates.end_time
    db_session.commit()
    db_session.refresh(tournament)
    return tournament


def validate_number_of_players(tournament: Tournament) -> bool:
    valid_count_players = (4, 8, 16, 32, 64, 128, 256, 512, 1024)
    total_players = len(tournament.participants)
    return total_players in valid_count_players


def randomize_players(tournament: Tournament) -> tuple[list[UUID], list[UUID]]:
    players_ids = []
    for participant in tournament.participants:
        players_ids.append(participant.id)

    random.shuffle(players_ids)
    return (
        players_ids[: len(tournament.participants) // 2],
        players_ids[len(tournament.participants) // 2 :],
    )


def get_tournament_format(tournament_id: UUID, db_session: Session):
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)
    return tournament.format.type


def create_matches(tournament_id: UUID, db_session: Session):
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)
    if tournament.format.type == "knockout":
        matches = _create_knockout_matches(tournament, db_session)
    
    return matches


def _create_match(
    db_session: Session,
    tournament: Tournament,
    player_a_id: UUID | None = None,
    player_b_id: UUID | None = None,
    stage: int | None = None,
    serial_number: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
):
    match = Match(
        format_id=tournament.match_format_id,
        player_a_id=player_a_id,
        player_b_id=player_b_id,
        score_a=0,
        score_b=0,
        start_time=start_time,
        end_time=end_time,
        author_id=tournament.author_id,  # TODO replace with current user
        tournament_id=tournament.id,
        stage=stage,
        serial_number=serial_number,
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


def _create_knockout_matches(tournament: Tournament, db_session: Session):
    if not validate_number_of_players(tournament):
        raise InvalidNumberOfPlayers(number_of_players=len(tournament.participants))

    all_matches = []
    players_group_1, players_group_2 = randomize_players(tournament)
    all_stages = calculate_stages(tournament)
    stage = 0
    serial_number = 0
    for player_a_id, player_b_id in zip(players_group_1, players_group_2):
        temp_match = _create_match(
            db_session, tournament, player_a_id, player_b_id, stage, serial_number
        )
        serial_number += 1
        all_matches.append(temp_match)

    number_of_stage_matches = len(tournament.participants) // 2
    for stage in range(1, all_stages):
        number_of_stage_matches = number_of_stage_matches // 2
        for serial_number in range(number_of_stage_matches):
            temp_match = _create_match(
                db_session, tournament, stage=stage, serial_number=serial_number
            )
            all_matches.append(temp_match)

    return all_matches


def calculate_stages(tournament: Tournament) -> int:
    total_players = len(tournament.participants)
    stages = 0
    while total_players > 1:
        stages += 1
        total_players = total_players // 2

    return stages
