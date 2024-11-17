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
    tournament_id = Column(UUID, ForeignKey("tournaments.id"), nullable=False)

    tournament = relationship("Tournament", back_populates="matches")

class MatchFormat(Base):
    __tablename__ = "match_format"
    id = Column(
        Integer,
        primary_key=True,
        unique=True,
        nullable=False,
        autoincrement=True,
    )
    name = Column(String(10), unique=True, nullable=False)
