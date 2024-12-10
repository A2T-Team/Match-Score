from src.schemas.tournament import TournamentSchema, Participant, UpdateTournamentRequest
from src.models.tournament import Tournament, TournamentFormat, TournamentParticipants
from src.models.match import Match, MatchFormat
from src.models.player import Player
from src.models.user import User, Role
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, and_
from src.common.custom_responses import AlreadyExists
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from src.common.custom_exceptions import (
    NotFound,
    InvalidNumberOfPlayers,
    InvalidRequest,
)
import random
from datetime import datetime
from itertools import combinations
import logging

logger = logging.getLogger(__name__)


def tournament_format_to_id(value: str, db_session: Session) -> int | None:
    """
    The function queries the database for a `TournamentFormat` record
    with a `type` matching the given value. If a matching record is found,
    its ID is returned. If no match is found, `None` is returned.
    """
    format = (
        db_session.query(TournamentFormat)
        .filter(TournamentFormat.type == value)
        .first()
    )
    if format is None:
        return None

    return format.id


def match_format_to_id(value: str, db_session: Session) -> int | None:
    """
    The function queries the database for a `MatchFormat` record
    with a `type` matching the given value. If a matching record
    is found, its ID is returned. If no match is found, `None` is returned
    """
    format = db_session.query(MatchFormat).filter(MatchFormat.type == value).first()
    if format is None:
        return None

    return format.id


def can_update_tournament(current_user: User, tournament: Tournament) -> bool:
    """
    Checks if the current user has access to the given tournament.

    Args:
       current_user (User): The user whose access is being checked
       tournament (Tournament): The tournament in question
       db_session (Session): The database session
    """
    if current_user.role is Role.ADMIN:
        return True
    if current_user.role is Role.DIRECTOR and current_user.id == tournament.author_id:
        return True
    
    return False

def create(
    tournament: TournamentSchema,
    current_user: User,
    db_session: Session,
) -> Tournament:
    """
    Create a new tournament in the database, using the provided TournamentSchema object
    and the current user ID.

    Parameters:
        tournament (TournamentSchema): An instance of the `TournamentSchema` class.
        current_user_id (UUID): The ID of the user creating the category.
        current_user (User): The authenticated user

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
        author_id=current_user.id,
    )
    db_session.add(db_tournament)
    db_session.commit()
    db_session.refresh(db_tournament)

    return db_tournament


def tournament_name_exists(db: Session, tournament_name: str) -> bool:
    """
    Check if a tournament with the given name exists in the database.
    """
    count = db.query(Tournament).filter(Tournament.name == tournament_name).count()
    return count > 0


def get_tournament(
    db_session: Session,
    tournament_id: UUID,
) -> Tournament | None:
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


def view_all_tournaments(
    db_session: Session,
    offset: int = 0,
    limit: int = 10,
    sort: str = None,
    search: str = None,
) -> list[Tournament]:
    """
    Retrieve a paginated list of tournaments with optional sorting and search filters.

    The function queries the `Tournament` table to return a list of tournaments.
    Results can be filtered by a search term, sorted by start time, and paginated using
    `offset` and `limit` parameters.
    """
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
    """
    Retrieve a participant from the `Player` table by matching
    their first and last name (case-insensitively).
    """
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


def create_player(db_session: Session, participant: Participant) -> Player:
    """
    Create a new player in the database, using the `first_name`
    and `last_name` of the player to be created, provided in the `Participant` object.
    """
    new_profile = Player(
        first_name=participant.first_name, last_name=participant.last_name
    )
    db_session.add(new_profile)
    db_session.commit()
    db_session.refresh(new_profile)

    return new_profile


def add_participants(
    db_session: Session, tournament_id: UUID, participants: list[Participant]
) -> dict[UUID, dict[str, str]]:
    """
    Add participants to a tournament and handle player creation if needed.

    This function processes a list of participants, checks if they already exist
    in the database, and associates them with a tournament. If a participant
    does not exist, a new player record is created. The function also ensures that
    tournament participants are added without duplication, rolling back on conflicts.

    Args:
        db_session (Session): The SQLAlchemy database session used for database operations.
        tournament_id (UUID): The ID of the tournament to which participants are being added.
        participants (list[Participant]): A list of `Participant` objects containing
                                          the `first_name` and `last_name` of the participants.

    Returns:
        dict[UUID, dict[str, str]]: A dictionary where each key is the player's ID (UUID),
                                    and each value is another dictionary containing:
                                      - `first_name`: The first name of the player.
                                      - `last_name`: The last name of the player.
                                      - `status`: A string indicating "Added" if the participant
                                                  was successfully added, or "Already exists"
                                                  if the participant was already in the tournament.
    """
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
    """
    The function checks if a given participant is already registered in a specific tournament.
    It first attempts to find the participant in the database using their details, and if found,
    queries the TournamentParticipants table to determine if the participant is associated with
    the specified tournament.
    """
        
    db_player = get_participant(db_session, participant)
    if db_player is None:
        return None

    tournament_participant = (
        db_session.query(TournamentParticipants)
        .filter(
            and_(
                TournamentParticipants.player_id == db_player.id,
                TournamentParticipants.tournament_id == tournament_id,
            )
        )
        .first()
    )
    return tournament_participant


def delete_players(
    db_session: Session, tournament_id: UUID, participants: list[Participant]
) -> dict[str, dict[str, str]]:
    """
    Remove participants from a tournament.

    The function removes a list of participants from a specified tournament. For each participant:
    - It checks if the participant is registered in the given tournament.
    - If found, the participant's association with the tournament is deleted.
    - If not found, the function notes that the participant was not registered in the tournament.

    Args:
        db_session (Session): The database session used for querying and committing changes.
        tournament_id (UUID): The unique identifier of the tournament from which participants will be removed.
        participants (list[Participant]): A list of participants to be removed, where each participant includes 
        first name and last name.

    Returns:
        dict: A dictionary containing the full names of participants as keys and their deletion statuses as values.
              Possible statuses are:
              - "Deleted": The participant was successfully removed from the tournament.
              - "Not Found": The participant was not registered in the specified tournament.
    """
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


def remove_player(
    db_session: Session, tournament_id: UUID, player_id: UUID
) -> None:
    """
    Remove participant from a tournament.

    The function removes a single participant from a specified tournament.
    - It checks if the participant is registered in the given tournament.
    - If found, the participant's association with the tournament is removed.
    - If not found, the function raises NotFound exception

    Args:
        db_session (Session): The database session used for querying and committing changes.
        tournament_id (UUID): The unique identifier of the tournament from which participants will be removed.
        player_id (UUID):  The unique identifier of the participant to be removed.

    Returns:
        None
    """
    tournament_participant = (
        db_session.query(TournamentParticipants)
        .filter(
            and_(
                TournamentParticipants.player_id == player_id,
                TournamentParticipants.tournament_id == tournament_id,
            )
        )
        .first()
    )
    if tournament_participant is None:
        raise NotFound(key="participant", key_value=player_id)

    db_session.delete(tournament_participant)
    db_session.commit()


def update_tournament(
    tournament_id: UUID, data: UpdateTournamentRequest, db_session: Session
) -> Tournament:
    """
    The function modifies the details of an existing tournament based on the provided data.
    It ensures that the new start and end times do not conflict with the timings of existing matches 
    in the tournament.

    Args:
        tournament_id (UUID): The unique identifier of the tournament to update.
        data (UpdateTournamentRequest): An object containing the fields to update. Possible fields include:
            - `name` (str): The new name of the tournament.
            - `start_time` (datetime): The new start time of the tournament.
            - `end_time` (datetime): The new end time of the tournament.
            - `prize` (str): The updated prize for the tournament.
        db_session (Session): The database session used for querying and committing changes.
    """
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)

    if data.name:
        tournament.name = data.name
    if data.start_time:
        for match in tournament.matches:
            if match.start_time and match.start_time < data.start_time:
                raise InvalidRequest("Tournament start time cannot be after its matches start time")
        tournament.start_time = data.start_time
    if data.end_time:
        for match in tournament.matches:
            if match.end_time and match.end_time > data.end_time:
                raise InvalidRequest("Tournament end time cannot be before its matches end time")
        tournament.end_time = data.end_time
    if data.prize:
        tournament.prize = data.prize
    db_session.commit()
    db_session.refresh(tournament)

    return tournament


def validate_number_of_players(tournament: Tournament) -> bool:
    valid_count_players = (4, 8, 16, 32, 64, 128, 256, 512, 1024)
    total_players = len(tournament.participants)
    return total_players in valid_count_players


def randomize_players(tournament: Tournament) -> tuple[list[UUID], list[UUID]]:
    """
    Randomly divide tournament participants into two groups.

    The function takes a tournament and splits its participants into two random groups of 
    equal size. The order of participants in each group is randomized.

    Args:
        tournament (Tournament): The tournament object containing the participants to be randomized.
                                 Each participant is expected to have a unique `id`.

    Returns:
        tuple[list[UUID], list[UUID]]: A tuple containing two lists:
            - The first list contains the IDs of players in the first group.
            - The second list contains the IDs of players in the second group.
    """
    players_ids = []
    for participant in tournament.participants:
        players_ids.append(participant.id)

    random.shuffle(players_ids)
    return (
        players_ids[: len(tournament.participants) // 2],
        players_ids[len(tournament.participants) // 2 :],
    )


def get_tournament_format(tournament_id: UUID, db_session: Session) -> str:
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)
    return tournament.format.type


def has_matches(tournament: Tournament) -> bool:
    return bool(tournament.matches)


def create_matches(tournament_id: UUID, db_session: Session, current_user: User) -> list[Match]:
    """
    Creates matches for the specified tournament based on its format.

    Returns:
        list[Match]: A list of `Match` objects representing all matches for the tournament.

    Raises:
        InvalidRequest: If the tournament already has matches.
        InvalidNumberOfPlayers: If the tournament has an invalid number of participants
                                for the chosen format (e.g., not a power of two for knockout).
    """
        
    tournament = get_tournament(db_session=db_session, tournament_id=tournament_id)
    if has_matches(tournament):
        raise InvalidRequest("Tournament already has matches")

    if tournament.format.type == "knockout":
        matches = _create_knockout_matches(tournament, db_session, current_user)
    elif tournament.format.type == "league":
        if not tournament.valid_number_of_players:
            raise InvalidNumberOfPlayers(
            number_of_players=len(tournament.participants), tournament_format="league"
        )
        matches = _create_league_matches(tournament, db_session, current_user)
    
    return matches


def _create_match(
    db_session: Session,
    tournament: Tournament,
    current_user: User,
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
        author_id=current_user.id,
        tournament_id=tournament.id,
        stage=stage,
        serial_number=serial_number,
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    return match


def calculate_stages(tournament: Tournament) -> int:
    total_players = len(tournament.participants)
    stages = 0
    while total_players > 1:
        stages += 1
        total_players = total_players // 2

    return stages


def _create_knockout_matches(
    tournament: Tournament, db_session: Session, current_user: User
) -> list[Match]:
    """
    Create matches for a knockout tournament.

    The function generates Matches for a knockout tournament,
    organizing matches in a tree-like structure where winners progress to the next round.

    Returns:
        list[Match]: A list of `Match` objects representing all the matches in the knockout tournament.
    """
        
    if not validate_number_of_players(tournament):
        raise InvalidNumberOfPlayers(
            number_of_players=len(tournament.participants), tournament_format="knockout"
        )

    all_matches = []
    players_group_1, players_group_2 = randomize_players(tournament)
    all_stages = calculate_stages(tournament)
    stage = 0
    serial_number = 0
    for player_a_id, player_b_id in zip(players_group_1, players_group_2):
        temp_match = _create_match(
            db_session,
            tournament,
            current_user,
            player_a_id,
            player_b_id,
            stage,
            serial_number,
        )
        serial_number += 1
        all_matches.append(temp_match)

    number_of_stage_matches = len(tournament.participants) // 2
    for stage in range(1, all_stages):
        number_of_stage_matches = number_of_stage_matches // 2
        for serial_number in range(number_of_stage_matches):
            temp_match = _create_match(
                db_session,
                tournament,
                current_user,
                stage=stage,
                serial_number=serial_number,
            )
            all_matches.append(temp_match)

    return all_matches


def _create_league_matches(
    tournament: Tournament, db_session: Session, current_user: User
) -> list[Match]:
    """
    Generate league matches for a tournament.

    The function creates Matches for a league tournament, ensuring that:
    - Every participant plays against every other participant exactly once.
    - Matches are organized into stages (rounds), where each player participates in one match per stage.

    Returns:
        list[Match]: A list of `Match` objects representing all the league matches.
    """

    if len(tournament.participants) < 3:
        raise InvalidNumberOfPlayers(
            number_of_players=len(tournament.participants), tournament_format="league"
        )

    players_ids = [participant.id for participant in tournament.participants]

    random.shuffle(players_ids)
    all_staged_matches = split_in_stages(players_ids)
    all_matches = []
    for stage, staged_matches in enumerate(all_staged_matches):
        for serial_number, pair in enumerate(staged_matches):
            temp_match = _create_match(
                db_session,
                tournament,
                current_user,
                player_a_id=pair[0],
                player_b_id=pair[1],
                stage=stage,
                serial_number=serial_number,
            )
            all_matches.append(temp_match)

    return all_matches


def split_in_stages(players_ids: list[UUID]) -> list[list[tuple[str, str]]]:
    """
    Split player pairs into stages.
    https://medium.com/moove-it/algorithm-for-the-generation-of-a-soccer-or-any-sport-or-event-fixture-c9798732121d

    The function organizes player pairs into a specified number of stages, ensuring that:
    - Each player participates in one match per stage.
    - All players play against every other player exactly once across all stages.

    Returns:
        list[list[tuple[str, str]]]: A list where each element represents a stage, 
        containing the matches (pairs of players) for that stage.
    """
    num_players = len(players_ids)
    num_stages = num_players - 1
    num_matches_per_stage = num_players // 2
    all_matches = []
    last_player = players_ids[-1]
    for stage in range(num_stages):
        stage_matches = []
        stage_players = []
        if stage == 0:
            for i in range(num_matches_per_stage):
                pair = (players_ids[i], players_ids[-1-i])
                stage_matches.append(pair)
                stage_players.extend(pair)
        else:
            previous_stage_last_player = previous_stage_players.pop()
            previous_stage_players.remove(last_player)
            if stage // 2 == 0:
                pair = (previous_stage_last_player, last_player)
            else:
                pair = (last_player, previous_stage_last_player)
            stage_matches.append(pair)
            stage_players.extend(pair)
            while previous_stage_players:
                player_b = previous_stage_players.pop()
                player_a = previous_stage_players.pop()
                pair = (player_a, player_b)
                stage_matches.append(pair)
                stage_players.extend(pair)

        previous_stage_players = stage_players
        all_matches.append(stage_matches)

    return all_matches


def split_in_stages_old(
    player_pairs: list[tuple[str, str]], num_players: int
) -> list[list[tuple[str, str]]]:
    """
    Split player pairs into stages.

    The function organizes player pairs into a specified number of stages, ensuring that:
    - Each player participates in one match per stage.
    - All players play against every other player exactly once across all stages.

    Returns:
        list[list[tuple[str, str]]]: A list where each element represents a stage, 
        containing the matches (pairs of players) for that stage.
    """

    num_stages = num_players - 1
    num_matches_per_stage = num_players // 2
    all_matches = []
    for _ in range(num_stages):
        stage_matches = []
        while len(stage_matches) < num_matches_per_stage:
            players_in_stage = set()
            while stage_matches:
                player_pairs.append(stage_matches.pop())
            random.shuffle(player_pairs)
            for _ in range(num_matches_per_stage):
                for player_a, player_b in player_pairs.copy():
                    if player_a in players_in_stage or player_b in players_in_stage:
                        continue
                    stage_matches.append((player_a, player_b))
                    players_in_stage.add(player_a)
                    players_in_stage.add(player_b)
                    player_pairs.remove((player_a, player_b))
                    break

        all_matches.append(stage_matches)

    return all_matches


def get_combinations(players: list[str]) -> list[tuple[str, str]]:
    """
    Generate all possible pair combinations from a list of players.

    The function returns a list of all unique pairs (2-player combinations) 
    that can be formed from the given list of players. Each pair is represented as a tuple.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple represents a unique pair of players.
    """
    return list(combinations(players, 2))


def delete_tournament(db_session, tournament_id):
        tournament = get_tournament(db_session, tournament_id)

        db_session.delete(tournament)
        db_session.commit()


def get_all_players(db: Session) -> list[Player]:
    players = db.query(Player).order_by(Player.first_name).all()
    
    return players

# def _create_league_matches_with_groups(
#     tournament: Tournament, db_session: Session, current_user: User
# ):
#     if len(tournament.participants) < 3:
#         raise InvalidNumberOfPlayers(number_of_players=len(tournament.participants))
#     if len(tournament.participants) >= 8:
#         groups = divide_players_into_groups(tournament)
#         all_matches = []
#         for index, group in enumerate(groups):
#             group_matches = []
#             for i in range(len(group)):
#                 for j in range(i + 1, len(group)):
#                     # Create a match between players i and j
#                     temp_match = _create_match(
#                         db_session,
#                         tournament,
#                         current_user,
#                         player_a_id=group[i],
#                         player_b_id=group[j],
#                         stage=index,
#                         serial_number=i,
#                     )
#                     group_matches.append(temp_match)
#             all_matches.append(group_matches)

#     return all_matches


# def divide_players_into_groups(tournament: Tournament) -> list[list[UUID]]:
#     groups = []
#     group_size = 4
#     players_ids = tournament.participants
#     random.shuffle(players_ids)

#     # Step 1: Divide players into initial groups of 4
#     for i in range(0, len(players_ids), group_size):
#         groups.append(players_ids[i : i + group_size])

#     # Step 2: Handle the last group if it has less than 3 players
#     if len(groups[-1]) < 3:
#         last_group = groups.pop()  # Remove the last group
#         # Redistribute players from the last group to earlier groups
#         for index, player_id in enumerate(last_group):
#             groups[index].append(player_id)

#     return groups
