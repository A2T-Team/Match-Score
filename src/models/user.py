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


class Role(Enum):

    """
    Enum representing the role of a user in the system.
    """

    USER = "user"
    PLAYER = "player"
    DIRECTOR = "director"
    ADMIN = "admin"


class User(Base):

    """
    Database model representing "users" table in the database.
    UUID and table name are inherited from BaseMixin.
    """

    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String)
    email = Column(String(50), unique=True, nullable=False)
    country = Column(String(50), nullable=False)
    role = Column(Role, nullable=False, default=Role.USER)


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
        "Tournament", secondary="tournament_participants", back_populates="participants"
    )
    match = relationship("Match", back_populates="author")
    author_of_player = relationship("Player", back_populates="author")
    user_as_player = relationship("Player", back_populates="user")