from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uuid
import re


class CreatePlayerRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, examples=["John"])
    last_name: str = Field(min_length=2, max_length=50, examples=["Doe"])
    country: str = Field(description="For which country the player competes")
    team_id: uuid.UUID = Field(description="Player's team")
    matches_played: int = Field(0, description="Matches played")
    wins: int = Field(0, description="Wins")
    losses: int = Field(0, description="Losses")
    draws: int = Field(0, description="Draws")
    poinnts: int = Field(0, description="Points")
    user_id: uuid.UUID = Field(description="User ID that relates to the player")

    @field_validator("first_name")
    def validate_first_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 50:
            raise ValueError("First name must be between 2 and 50 characters")
        if not re.match(r"^[A-Za-z\s\-]+$", value):
            raise ValueError("First name must contain only alphabetic characters, dashes, or spaces")
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 50:
            raise ValueError("Last name must be between 2 and 50 characters")
        if not re.match(r"^[A-Za-z\s\-]+$", value):
            raise ValueError("Last name must contain only alphabetic characters, dashes, or spaces")
        return value

    @field_validator("country")
    def validate_country(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 50:
            raise ValueError("Country must be between 2 and 50 characters")
        return value

    @field_validator("matches_played", "wins", "losses", "draws", "points")
    def validate_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None

class PlayerResponse(CreatePlayerRequest):
    id: uuid.UUID = Field(..., description="Unique ID of the player")

    model_config = {
        "from_attributes": True,  # Enables ORM mode
    }