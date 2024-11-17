from src.models.base import Base, BaseMixin
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


class User(Base, BaseMixin):
    """
    Database model representing "users" table in the database.
    UUID and table name are inherited from BaseMixin.
    """
    __tablename__ = "users"

    username = Column(String)
    password = Column(String)


class Team(Base):
    __tablename__ = "teams"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(50), unique=True, nullable=False)
    matches_played = Column(Integer, nullable=False, default=0)


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
    team_id = Column(UUID, ForeignKey("teams.id"), nullable=True)
    matches_played = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    author_id = Column(UUID, ForeignKey("users.id"), nullable=True)

    tournament = relationship(
        "Tournament", secondary="TournamentParticipants", back_populates="participants"
    )
