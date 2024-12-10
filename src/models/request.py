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

from src.models.player import Player


class RequestAction(PyEnum):

    """
    Enum representing the action to be taken on a request.
    """

    ACCEPT = "Accept"
    REJECT = "Reject"


class RequestType(PyEnum):

    """
    Enum representing the type of request.
    """

    PROMOTE = "Promote Request"
    DEMOTE = "Demote Request"
    LINK = "Link Request"
    UNLINK = "Unlink Request"


class RequestStatus(PyEnum):

    """
    Enum representing the status of a request.
    """

    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class Requests(Base):

    """
    Database model representing "requests" table in the database.
    """

    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type = Column(Enum(RequestType, name="request_enum"), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    status = Column(Enum(RequestStatus, name="request_status_enum"),
                    default=RequestStatus.PENDING, nullable=False)
