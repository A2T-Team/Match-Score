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
from src.models.match import Match


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
    country = Column(String(50))
    team_id = Column(UUID, nullable=True)
    matches_played = Column(Integer, default=0, nullable=True)
    wins = Column(Integer, default=0, nullable=True)
    losses = Column(Integer, default=0, nullable=True)
    draws = Column(Integer, default=0, nullable=True)
    #points = Column(Integer, default=0, nullable=True)
    #author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)

    # user = relationship("User", back_populates="user_as_player")
    matches_as_a = relationship("Match", foreign_keys="Match.player_a_id", back_populates="player_a", lazy='dynamic')
    matches_as_b = relationship("Match", foreign_keys="Match.player_b_id", back_populates="player_b", lazy='dynamic')
    tournament = relationship("Tournament", secondary="tournament_participants", back_populates="participants")
