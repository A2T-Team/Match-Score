from pydantic import BaseModel, Field, field_validator
from src.models.request import RequestType, RequestStatus
import uuid
from datetime import datetime


class CreateRequest(BaseModel):

    """
    Schema for creating a new request.
    """

    type: RequestType = Field(examples=["Promote Request", "Demote Request", "Delete Request",
                                        "Link Request", "Unlink Request"])
    reason: str = Field(min_length=10, max_length=100, examples=["If you want to link your account to a player,"
                                                                 " write only the player's firstname"
                                                                 " and lastname here."])

    @field_validator("reason")
    def validate_request_reason(cls, value):

        """
        Validate request_data to be a string.
        """

        if not isinstance(value, str):
            raise ValueError("Reason must be a string")
        return value


class RequestResponse(BaseModel):

    """
    Schema for returning request data.
    """

    id: uuid.UUID
    type: RequestType
    user_id: uuid.UUID
    reason: str
    created_at: datetime
    status: RequestStatus
