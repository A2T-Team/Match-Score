from fastapi import APIRouter, Depends, Query, Path
from src.schemas.tournament import CreateTournamentRequest
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from src.common.custom_responses import AlreadyExists, InternalServerError
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.crud import tournaments
import logging

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/", status_code=200)
def create_tournament(
    tournament: CreateTournamentRequest, db_session: Session = Depends(get_db) #current_user_id: int = Depends(get_current_user)
):
    """
    Create new tournament with the provided details. Access is restricted to users
    with admin or director role. If a tournament with the same name already exists, a BadRequest 
    response is returned.

    Parameters:
        tournament (CreateTournamentRequest): The request body containing the details of the tournament 
        to be created: 
            name (min_length 5, max_length 50), 
            format ('league' or 'knockout'), 
            match_format ('time' or 'score'),
            start_time ('YYYY/MM/DD HH:MM'),
            end_time ('YYYY/MM/DD HH:MM')
            prize (int: 0 or positive),
            win_points (How many points the winner gets),
            draw_points (How many points the players get on draw).
        current_user_id (int): The ID of the currently authenticated user, provided by the
        authentication dependency.

    Returns:
        Response: details containing the created tournament or appropriate error messages.
    """
    try:
        return tournaments.create(tournament=tournament, db_session=db_session)
    
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            if "tournaments_name_key" in str(e.orig):
                return AlreadyExists(f"Tournament with name '{tournament.name}'")
            else:
                return InternalServerError(f"An unexpected integrity error occurred: {str(e)}") 
        return InternalServerError(f"Database error: {str(e)}") 

