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

    format_id = Column(Integer, ForeignKey("match_format.id"), nullable = False)
    player_a_id = Column(UUID, ForeignKey("players.id"))
    player_b_id = Column(UUID, ForeignKey("players.id"))
    score_a = Column(Integer)
    score_b = Column(Integer)
    result_code = Column(Integer, ForeignKey("result_codes.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    prize = Column(Integer)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(UUID, ForeignKey("tournaments.id"))
    stage = Column(Integer)
    serial_number = Column(Integer)

    tournament = relationship("Tournament", back_populates="matches")
    player_a = relationship("Player", foreign_keys=[player_a_id], back_populates="matches_as_a")
    player_b = relationship("Player", foreign_keys=[player_b_id], back_populates="matches_as_b")
    # match_format = relationship("MatchFormat", back_populates="match")
    # author = relationship("User", back_populates="match")
    result = relationship("ResultCodes", back_populates="match")

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
    tournaments = relationship("Tournament", back_populates="match_format")


    #matches = relationship("Match", back_populates="match_format")

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