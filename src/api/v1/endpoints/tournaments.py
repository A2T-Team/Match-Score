from fastapi import APIRouter, Depends, Query, Path
from schemas.tournament import CreateTournamentRequest
from sqlalchemy.orm import Session
from deps import get_db
from crud.tournaments import create


tournament_router = APIRouter(prefix="/api/v1/tournament", tags=["Tournament"])


@tournament_router.post("/", status_code=201)
def create_tournament(
    tournament: CreateTournamentRequest, db: Session = Depends(get_db) #current_user_id: int = Depends(get_current_user)
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

    return create(tournament=tournament, db=db)


@tournament_router.get("/")
def read_users():
    pass
