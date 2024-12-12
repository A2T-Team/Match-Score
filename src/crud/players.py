from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from src.models.player import Player
from src.models.user import User
from src.models.tournament import TournamentParticipants

from src.schemas.player import CreatePlayerRequest, PlayerUpdate


def create_player(db: Session, request: CreatePlayerRequest):
    """Create a new player in the database.
    
    Args:
        db (Session): The database session.
        request (CreatePlayerRequest): The request data for creating a new player.
    
    Returns:
        Player: The newly created player.
    """
    new_player = Player(**request.model_dump())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


def read_player_by_id(db: Session, player_id: UUID):
    """Retrieve a player by their unique ID.
    
    Args:
        db (Session): The database session.
        player_id (UUID): The unique identifier of the player.
    
    Raises:
        HTTPException: If the player is not found.
    
    Returns:
        Player: The player matching the given ID.
    """
    player = db.query(Player).filter_by(id=player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return player

def read_current_user_player_profile(db:Session, user: User):
    """Retrieve the player profile associated with the current user.
    
    Args:
        db (Session): The database session.
        user (User): The current authenticated user.
    
    Raises:
        HTTPException: If no player profile is associated with the user.
    
    Returns:
        Player: The player profile linked to the current user.
    """
    player = db.query(Player).filter_by(user_id = user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no Player profile"
        )
    return player

def read_all_players(db: Session, tournament_id: UUID | None = None):
    """Retrieve all players, optionally filtered by tournament.
    
    Args:
        db (Session): The database session.
        tournament_id (UUID, optional): The ID of the tournament to filter players.
    
    Returns:
        list[Player]: A list of all players, optionally filtered by tournament.
    """
    query = db.query(Player)
    
    if tournament_id:
        query = (
            query.join(TournamentParticipants, Player.id == TournamentParticipants.player_id)
            .filter(TournamentParticipants.tournament_id == tournament_id)
        )
    query = query.order_by(Player.first_name)
    
    return query.all()


def update_player(db: Session, player_id: UUID, updates: PlayerUpdate, current_user: User) -> Player:
    """Update an existing player's information.
    
    Args:
        db (Session): The database session.
        player_id (UUID): The unique identifier of the player to be updated.
        updates (PlayerUpdate): The fields to update for the player.
        current_user (User): The user requesting the update.
    
    Raises:
        HTTPException: If the player is not found or the user is not authorized to update the player.
    
    Returns:
        Player: The updated player.
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
                )
    if player.user_id and (player.user_id != current_user.id or current_user.role != 'USER'):
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't update player"
                )
    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(player, key, value)
    db.commit()
    db.refresh(player)

    return player


def delete_player(db: Session, player_id: UUID, current_user: User):
    """Delete a player from the database.
    
    Args:
        db (Session): The database session.
        player_id (UUID): The unique identifier of the player to be deleted.
        current_user (User): The user requesting the deletion.
    
    Raises:
        HTTPException: If the player is not found or the user is not authorized to delete the player.
    
    Returns:
        bool: True if the player was successfully deleted.
    """
    player = db.query(Player).filter_by(id=player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    if (player.user_id and player.user_id != current_user.id) and current_user.role != 'ADMIN':
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Current user can't delete player"
                )
    db.delete(player)
    db.commit()
    return True

def update_player_with_user(db: Session, player_id: UUID, user_id: UUID):
    """Associate a player with a user account.
    
    Args:
        db (Session): The database session.
        player_id (UUID): The unique identifier of the player.
        user_id (UUID): The unique identifier of the user.
    
    Raises:
        HTTPException: If the player or user is not found.
    
    Returns:
        Player: The player with the updated user association.
    """
    player = db.query(Player).filter_by(id=player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    player.user_id = user_id
    db.commit()
    db.refresh(player)
    return player


def read_player_by_id_and_tournament(db: Session, player_id: UUID, tournament_id: UUID):
    """Retrieve detailed player information for a specific tournament.
    
    Args:
        db (Session): The database session.
        player_id (UUID): The unique identifier of the player.
        tournament_id (UUID): The unique identifier of the tournament.
    
    Raises:
        HTTPException: If the player is not found in the specified tournament.
    
    Returns:
        dict: A dictionary containing player and tournament details.
    """
    player = (
        db.query(
            Player.id,
            Player.first_name,
            Player.last_name,
            Player.country,
            Player.team_id,
            Player.matches_played,
            Player.wins,
            Player.losses,
            Player.draws,
            Player.user_id,
            TournamentParticipants.tournament_id,
            TournamentParticipants.score,
            TournamentParticipants.stage
        )
        .join(TournamentParticipants, Player.id == TournamentParticipants.player_id)
        .filter(Player.id == player_id, TournamentParticipants.tournament_id == tournament_id)
        .first()
    )

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Player not found in the specified tournament"
        )
    
    player_data = {
        "id": player.id,
        "first_name": player.first_name,
        "last_name": player.last_name,
        "country": player.country,
        "team_id": player.team_id,
        "matches_played": player.matches_played,
        "wins": player.wins,
        "losses": player.losses,
        "draws": player.draws,
        "user_id": player.user_id,
        "tournament_id": player.tournament_id,
        "score": player.score,
        "stage": player.stage
    }
    
    return player_data