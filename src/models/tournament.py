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
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False)

    matches = relationship(
        "Match", back_populates="tournament"
    )  # To add in class Match -> tournament = relationship("Tournament", back_populates="matches")
    participants = relationship(
        "Player", secondary="tournament_participants", back_populates="tournament"
    )  # To add in class Player -> tournament = relationship("Tournament", secondary="TournamentParticipants", back_populates="participants")
    format = relationship("TournamentFormat", back_populates="tournaments")
    match_format = relationship("MatchFormat", back_populates="tournaments")

    def __repr__(self):
        return f"Tournament '{self.name}', start date '{self.start_time}', end date '{self.end_time}')"
    
    @property
    def valid_number_of_players(self) -> bool:
        if self.format_id == 0:
            valid_count_players = (4, 8, 16, 32, 64, 128, 256, 512, 1024)
            return len(self.participants) in valid_count_players
        else:
            return len(self.participants) >= 4 and len(self.participants)%2 == 0
    
    @property
    def num_stages(self) -> int:
        if self.format_id == 0:
            if self.valid_number_of_players:
                total_players = len(self.participants)
                stages = 0
                while total_players > 1:
                    stages += 1
                    total_players = total_players // 2
                return stages
            else:
                return 0
        else:
            if self.valid_number_of_players:
                return len(self.participants) - 1
            else:
                return 0


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
    type = Column(String(10), unique=True, nullable=False)

    tournaments = relationship("Tournament", back_populates="format")