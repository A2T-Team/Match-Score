from pydantic import BaseModel, Field, field_validator
from src.models.request import RequestType
import uuid
from datetime import datetime


class CreateRequest(BaseModel):

    """
    Schema for creating a new request.
    """

    request_type: RequestType = Field(examples=["Promote Request", "Demote Request", "Delete Request",
                                                "Link Request", "Unlink Request"])
    request_reason: str = Field(min_length=10, max_length=100, examples=["If you want to link your account to a player,"
                                                                         " write only the player's firstname"
                                                                         " and lastname here."])

    @field_validator("request_reason")
    def validate_request_reason(cls, value):

        """
        Validate request_data to be a string.
        """

        if not isinstance(value, str):
            raise ValueError("Request reason must be a string")
        return value


class RequestResponse(BaseModel):

    """
    Schema for returning request data.
    """

    request_id: uuid.UUID
    request_type: RequestType
    user_id: uuid.UUID
    request_reason: str
    created_at: datetime
