from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from src.schemas.tournament import (
    TournamentSchema,
    CreateTournamentResponse,
    Participant,
    UpdateTournamentDates,
    UpdateDatesResponse,
)
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from src.common.custom_responses import (
    AlreadyExists,
    InternalServerError,
    NotFound,
    NoContent,
    Unauthorized,
    ForbiddenAccess,
    BadRequest,
)
from src.common import custom_exceptions
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.crud import tournaments
from uuid import UUID
from src.core.auth import get_current_user
from src.models.user import User, Role

import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/", status_code=201)
def create_tournament(
    tournament: TournamentSchema,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new tournament. Only accessible to users with admin or director roles.

    Args:
    tournament (TournamentSchema): Tournament details to be created.
    db_session (Session): Database session (injected).
    current_user (User): The authenticated user (injected).

    Returns:
    The created tournament details or appropriate error messages.
    """

    if current_user is None:
        raise Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        raise ForbiddenAccess()

    try:
        return tournaments.create(
            tournament=tournament, current_user=current_user, db_session=db_session
        )

    except custom_exceptions.NotFound as e:
        return NotFound(key=e.key, key_value=e.key_value)

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            if "tournaments_name_key" in str(e.orig):
                return AlreadyExists(f"Tournament with name '{tournament.name}'")
            else:
                return InternalServerError(
                    f"An unexpected integrity error occurred: {str(e)}"
                )
        return InternalServerError(f"Database error: {str(e)}")


@router.get("/{tournament_id}")
def view_tournament(tournament_id: UUID, db_session: Session = Depends(get_db)):

    tournament = tournaments.get_tournament(db_session, tournament_id)
    if tournament is None:
        return NotFound(key="tournament_id", key_value=tournament_id)

    response = CreateTournamentResponse(
        tournament_id=tournament.id,
        name=tournament.name,
        format=tournament.format.type,
        match_format=tournament.match_format.type,
        start_time=tournament.start_time,
        end_time=tournament.end_time,
        prize=tournament.prize,
        win_points=tournament.win_points,
        draw_points=tournament.draw_points,
        author_id=tournament.author_id,
        total_participants=len(tournament.participants),
        participants=[
            {
                "player_id": participant.id,
                "full_name": (f"{participant.first_name} {participant.last_name}"),
            }
            for participant in tournament.participants
        ],
        total_matches=len(tournament.matches),
        matches=[
            {
                "match_id": match.id,
                "match_name": (
                    f"{match.player_a.first_name} {match.player_a.last_name}"
                    f" vs {match.player_b.first_name} {match.player_b.last_name}",
                ),
            }
            for match in tournament.matches
        ],
    )
    return response


@router.get("/")
def view_all_tournaments(
    offset: int = 0,
    limit: int = 100,
    sort: str = None,
    search: str = None,
    db_session: Session = Depends(get_db),
):
    return tournaments.view_all_tournaments(
        db_session, offset=offset, limit=limit, sort=sort, search=search
    )


@router.put("/{tournament_id}/players")
def add_players(
    tournament_id: UUID,
    participants: list[Participant],
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        raise ForbiddenAccess()

    tournament = tournaments.get_tournament(
        db_session,
        tournament_id,
    )
    if tournament is None:
        return NotFound(key="tournament_id", key_value=tournament_id)

    result = tournaments.add_participants(db_session, tournament_id, participants)
    return result


@router.delete("/{tournament_id}/players")
def delete_players(
    tournament_id: UUID,
    participants: list[Participant],
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        raise ForbiddenAccess()

    tournament = tournaments.get_tournament(
        db_session,
        tournament_id,
    )
    if tournament is None:
        return NotFound(key="tournament_id", key_value=tournament_id)

    result = tournaments.delete_players(db_session, tournament_id, participants)
    return result


@router.put("/{tournament_id}/dates")
def update_tournament_dates(
    tournament_id: UUID,
    dates: UpdateTournamentDates,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        raise ForbiddenAccess()

    tournament = tournaments.get_tournament(
        db_session,
        tournament_id,
    )

    if tournament is None:
        return NotFound(key="tournament_id", key_value=tournament_id)

    tournament = tournaments.update_dates(tournament_id, dates, db_session)

    response = UpdateDatesResponse(
        tournament_id=tournament.id,
        name=tournament.name,
        format=tournament.format.type,
        start_time=tournament.start_time,
        end_time=tournament.end_time,
    )
    return response


@router.put("/{tournament_id}/matches")
def create_matches(
    tournament_id: UUID,
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise Unauthorized(content="The user is not authorized to perform this action")

    if current_user.role not in {Role.ADMIN, Role.DIRECTOR}:
        raise ForbiddenAccess()

    tournament = tournaments.get_tournament(
        db_session,
        tournament_id,
    )
    if tournament is None:
        return NotFound(key="tournament_id", key_value=tournament_id)

    try:
        matches = tournaments.create_matches(tournament_id, db_session)
    except (
        custom_exceptions.InvalidNumberOfPlayers,
        custom_exceptions.InvalidRequest,
    ) as e:
        return BadRequest(content=str(e))

    return [
        {
            "match_id": match.id,
            "stage": match.stage,
            "serial": match.serial_number,
            "player_a_full_name": (
                f"{match.player_a.first_name} {match.player_a.last_name}"
                if match.player_a_id
                else "tbd"
            ),
            "player_b_full_name": (
                f"{match.player_b.first_name} {match.player_b.last_name}"
                if match.player_b_id
                else "tbd"
            ),
        }
        for match in matches
    ]


@router.put("/{tournament_id}/matches/{match_id}")
def update_match(
    tournament_id: UUID,
    players: list[str],
    db_session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pass
