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


class Match(Base):
    __tablename__ = "matches"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    format_id = Column(UUID, ForeignKey("match_format.id"), nullable = False)
    player_a = Column(UUID, ForeignKey("players.id"), nullable=False)
    player_b = Column(UUID, ForeignKey("players.id"), nullable=False)
    score_a = Column(Integer, default=0, nullable=True)
    score_b = Column(Integer, default=0, nullable=True)
    result_code = Column(Integer, ForeignKey("result_codes"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    #prize = Column(Integer, nullable=True)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(UUID, ForeignKey("tournaments.id"), nullable=False)

    tournament = relationship("Tournament", back_populates="matches")
    player_a = relationship("Player", foreign_keys=[player_a], back_populates="matches_as_a")
    player_b = relationship("Player", foreign_keys=[player_b], back_populates="matches_as_b")
    match_format = relationship("MatchFormat", back_populates="match")
    author = relationship("User", back_populates="match")
    result = relationship("ResultCode", back_populates="match")

class MatchFormat(Base):
    __tablename__ = "match_format"
    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    type = Column(String(10), unique=True, nullable=False)


    matches = relationship("Match", back_populates="match_format")

class ResultCodes(Base):
    __tablename__ = "result_codes"
    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    result = Column(String(10), unique=True, nullable=False)

    match = relationship("Match", back_populates="result")