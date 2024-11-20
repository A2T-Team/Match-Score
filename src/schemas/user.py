from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional
import re
import uuid


class CreateUserRequest(BaseModel):

    """
    Schema for creating a new user.
    """

    username: str = Field(min_length=5, max_length=50, examples=["johndoe"])
    email: str = Field(min_length=6, max_length=50, examples=["johndoe@gmail.com"])
    password: str = Field(min_length=8, max_length=50, examples=["password"])
    country: str = Field(min_length=3, max_length=50, examples=["USA"])

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

        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", value):
            raise ValueError("Password must be at least 8 characters long"
                             " and contain at least one letter and one number")
        return value

    @field_validator("country")
    def validate_country(cls, value):

        """
        Validate country to contain only letters.
        """

        if not re.match(r"^[a-zA-Z]+$", value):
            raise ValueError("Country must contain only letters")
        return value


class UpdateUserRequest(BaseModel):

    """
    Schema for updating user data.
    """

    email: Optional[str] = Field(min_length=6, max_length=50, examples=["johndoe@gmail.com"])
    role: Optional[str] = Field(examples=["user", "player", "director", "admin"])
