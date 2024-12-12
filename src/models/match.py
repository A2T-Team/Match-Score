from src.models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String
)
from sqlalchemy.orm import relationship


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
    end_condition = Column(Integer)
    player_a_id = Column(UUID, ForeignKey("players.id"))
    player_b_id = Column(UUID, ForeignKey("players.id"))
    score_a = Column(Integer)
    score_b = Column(Integer)
    result_code = Column(Integer, ForeignKey("result_codes.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    prize = Column(Integer)
    author_id = Column(UUID,  nullable=True)
    tournament_id = Column(UUID, ForeignKey("tournaments.id"))
    stage = Column(Integer)
    serial_number = Column(Integer) 

    tournament = relationship("Tournament", back_populates="matches")
    player_a = relationship("Player", foreign_keys=[player_a_id], back_populates="matches_as_a", lazy='select')
    player_b = relationship("Player", foreign_keys=[player_b_id], back_populates="matches_as_b", lazy='select')
    match_format = relationship("MatchFormat", back_populates="matches")
    result = relationship("ResultCodes", back_populates="match")

class MatchFormat(Base):
    __tablename__ = "match_format"
    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False
    )
    type = Column(String(10), unique=True, nullable=False)

    tournaments = relationship("Tournament", back_populates="match_format")
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