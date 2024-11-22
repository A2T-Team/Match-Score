from src.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship, validates


class Player(Base):
    __tablename__ = "players"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    team_id = Column(UUID, nullable=True)
    matches_played = Column(Integer, default=0, nullable=True)
    wins = Column(Integer, default=0, nullable=True)
    losses = Column(Integer, default=0, nullable=True)
    draws = Column(Integer), default=0, nullable=True
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    #author_id = Column(Integer, ForeignKey("users.id"), nullable=False)





    author = relationship("User", back_populates="author_of_player")
    user = relationship("User", back_populates="user_as_player")
    matches_as_a = relationship("Match", foreign_keys="[Match.player_a]", back_populates="player_a")
    matches_as_b = relationship("Match", foreign_keys="[Match.player_b]", back_populates="player_b")
    tournament = relationship("Tournament", secondary="TournamentParticipants", back_populates="participants")

