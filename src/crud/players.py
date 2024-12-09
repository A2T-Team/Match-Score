from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from src.models.player import Player
from src.models.user import User
from src.models.tournament import TournamentParticipants
#from src.models.match import Match

from src.schemas.player import CreatePlayerRequest, PlayerUpdate


def create_player(db: Session, request: CreatePlayerRequest):
    # # Check if the team exists
    # team = db.query(Team).filter_by(id=request.team_id).first()
    # if not team:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Team with ID {request.team_id} not found"
    #     )

    # Check if the user exists
    # user = db.query(User).filter_by(id=request.user_id).first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"User with ID {request.user_id} not found"
    #     )

    # Create the player
    # new_player = Player(
    #     first_name=request.first_name,
    #     last_name=request.last_name,
    #     country=request.country,
    #     team_id=request.team_id,
    #     matches_played=request.matches_played,
    #     wins=request.wins,
    #     losses=request.losses,
    #     draws=request.draws,
    #     user_id=request.user_id,
    # )
    new_player = Player(**request.model_dump())
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


def read_player_by_id(db: Session, player_id: UUID):
    player = db.query(Player).filter_by(id=player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    return player

def read_current_user_player_profile(db:Session, user: User):
    player = db.query(Player).filter_by(user_id = user.id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no Player profile"
        )
    return player

def read_all_players(db: Session, tournament_id: UUID | None = None):
    query = db.query(Player)
    
    if tournament_id:
        query = (
            query.join(TournamentParticipants, Player.id == TournamentParticipants.player_id)
            .filter(TournamentParticipants.tournament_id == tournament_id)
        )
    query = query.order_by(Player.first_name)
    
    return query.all()


# def update_player(db: Session, player_id: int, updates: PlayerUpdate):
#     player = db.query(Player).filter_by(id=player_id).first()
#     if not player:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Player not found"
#         )

#     if updates.first_name is not None:
#         player.first_name = updates.first_name
#     if updates.last_name is not None:
#         player.last_name = updates.last_name
#     if updates.country is not None:
#         player.country = updates.country
#     # if updates.team_id is not None:
#     #     team = db.query(Team).filter_by(id=updates.team_id).first()
#     #     if not team:
#     #         raise HTTPException(
#     #             status_code=status.HTTP_404_NOT_FOUND,
#     #             detail=f"Team with ID {updates.team_id} not found"
#     #         )
#     #     player.team_id = updates.team_id
#     if updates.matches_played is not None:
#         player.matches_played = updates.matches_played
#     if updates.wins is not None:
#         player.wins = updates.wins
#     if updates.losses is not None:
#         player.losses = updates.losses
#     if updates.draws is not None:
#         player.draws = updates.draws

#     db.commit()
#     db.refresh(player)
#     return player

def update_player(db: Session, player_id: UUID, updates: PlayerUpdate, current_user: User) -> Player:
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

    # Connect user to player
    player.user_id = user_id
    db.commit()
    db.refresh(player)
    return player


def read_player_by_id_and_tournament(db: Session, player_id: UUID, tournament_id: UUID):
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