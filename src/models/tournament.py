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
from sqlalchemy.sql import func


class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(50), unique=True, nullable=False)
    format_id = Column(Integer, ForeignKey("tournament_format.id"), nullable=False)
    match_format_id = Column(Integer, ForeignKey("match_format.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    prize = Column(Integer, nullable=False)
    win_points = Column(Integer, nullable=True)
    draw_points = Column(Integer, nullable=True)

    matches = relationship(
        "Match", back_populates="tournament"
    )  # To add in class Match -> tournament = relationship("Tournament", back_populates="matches")
    participants = relationship(
        "Player", secondary="TournamentParticipants", back_populates="tournament"
    )  # To add in class Player -> tournament = relationship("Tournament", secondary="TournamentParticipants", back_populates="participants")

    def __repr__(self):
        return f"Tournament '{self.name}', start date '{self.start_time}', end date '{self.end_time}')"


class TournamentParticipants(Base):
    __tablename__ = "tournament_participants"
    tournament_id = Column(UUID, ForeignKey("tournaments.id"), primary_key=True)
    player_id = Column(UUID, ForeignKey("players.id"), primary_key=True)
    score = Column(Integer, nullable=True)
    stage = Column(String(50), nullable=True)


class TournamentFormat(Base):
    __tablename__ = "tournament_format"
    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column(String(10), unique=True, nullable=False)
