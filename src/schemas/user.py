from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from src.models.user import Role, RequestType
from typing import Optional
import re
import uuid
from datetime import datetime


class CreateUserRequest(BaseModel):

    """
    Schema for creating a new user.
    """

    username: str = Field(min_length=5, max_length=50, examples=["johndoe"])
    email: str = Field(min_length=6, max_length=50, examples=["johndoe@gmail.com"])
    password: str = Field(min_length=8, max_length=50, examples=["password"])

    @field_validator("email")
    def validate_email(cls, value):

        """
        Validate email to contain '@' and '.'.
        """

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email address")
        return value

    @field_validator("password")
    def validate_password(cls, value):

        """
        Validate password to contain at least one letter and one number.
        """

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&\-_])[A-Za-z\d@$!%*?&\-_]{8,}$", value):
            raise ValueError("Password must be at least 8 characters long"
                             " and contain at least one letter and one number and one special character")
        return value


class UpdateEmailRequest(BaseModel):

    """
    Schema for updating user data.
    """

    email: Optional[str] = Field(min_length=6, max_length=50, examples=["johndoe@gmail.com"])

    @field_validator("email")
    def validate_email(cls, value):

        """
        Validate email to contain '@' and '.'.
        """

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email address")
        return value


class LoginRequest(BaseModel):

    """
    Schema for logging in a user.
    """

    username: str = Field(min_length=5, max_length=50, examples=["johndoe"])
    password: str = Field(min_length=8, max_length=50, examples=["password"])

    @field_validator("username")
    def validate_username(cls, value):

        """
        Validate username to contain only alphanumeric characters.
        """

        if not re.match(r"^[a-zA-Z0-9_]*$", value):
            raise ValueError("Username must contain only alphanumeric characters")
        return value

    @field_validator("password")
    def validate_password(cls, value):

        """
        Validate password to contain at least one letter and one number.
        """

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&\-_])[A-Za-z\d@$!%*?&\-_]{8,}$", value):
            raise ValueError("Password must be at least 8 characters long"
                             " and contain at least one letter and one number and one special character")
        return value


class UserResponse(BaseModel):

    """
    Schema for returning user data.
    """

    username: str
    email: str
    role: Role


class UpdateUserRequest(BaseModel):

    """
    Schema for updating user data.
    """

    email: Optional[str] = Field(min_length=6, max_length=50, examples=["johndoe@gmail.com"])
    role: Optional[str] = Field(examples=["user", "player", "director", "admin"])

    @field_validator("email")
    def validate_email(cls, value):

        """
        Validate email to contain '@' and '.'.
        """

        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Invalid email address")
        return value

    @field_validator("role")
    def validate_role(cls, value):

        """
        Validate role to be one of the predefined roles.
        """

        if value not in ["user", "player", "director", "admin"]:
            raise ValueError("Invalid role")
        return value


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
    def validate_request_data(cls, value):
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


