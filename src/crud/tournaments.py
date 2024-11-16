from schemas.tournament import CreateTournamentRequest
from models.tournament import Tournament
from sqlalchemy.orm import Session


def tournament_format_to_id(value):
    return 1 if value == "league" else 0

def match_format_to_id(value):
    return 1 if value == "score" else 0
    
def create(tournament: CreateTournamentRequest, db: Session, #current_user_id: int
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

    db_category = Tournament(
        name=tournament.name,
        format_id=tournament_format_to_id(tournament.format),
        match_format_id=match_format_to_id(tournament.match_format),
        start_time=tournament.start_time,
        end_time=tournament.end_time,
        prize=tournament.prize,
        win_points=tournament.win_points,
        draw_points=tournament.draw_points
    )   

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category