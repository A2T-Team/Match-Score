from src.models.base import Base, BaseMixin
import uuid
from enum import Enum as PyEnum
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
from datetime import datetime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func


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


class RequestType(PyEnum):
    PROMOTE = "Promote Request"
    DEMOTE = "Demote Request"
    DELETE = "Delete Request"
    LINK = "Link Request"
    UNLINK = "Unlink Request"


class Requests(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_type = Column(Enum(RequestType, name="request_enum"), nullable=False)
    request_reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
