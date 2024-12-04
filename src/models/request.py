from src.models.base import Base
import uuid
from enum import Enum as PyEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Text,
    Column,
    Enum,
    ForeignKey,
    DateTime
)
from datetime import datetime


class RequestType(PyEnum):

    """
    Enum representing the type of request.
    """

    PROMOTE = "Promote Request"
    DEMOTE = "Demote Request"
    DELETE = "Delete Request"
    LINK = "Link Request"
    UNLINK = "Unlink Request"


class Requests(Base):

    """
    Database model representing "requests" table in the database.
    """

    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    request_type = Column(Enum(RequestType, name="request_enum"), nullable=False)
    request_reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)