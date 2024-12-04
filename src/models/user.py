from src.models.base import Base
import uuid
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    String,
)


class Role(PyEnum):

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
    role = Column(Enum(Role, name="role_enum"), nullable=False, default=Role.USER)
