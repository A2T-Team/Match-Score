from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import uuid


class CreatePlayerRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, examples=["John"])
    last_name: str = Field(min_length=2, max_length=50, examples=["Doe"])
    country: str = Field(description="For which country the player competes")
    team_id: int = Field(description="Player's team")
    matches_played: int = Field(0, description="Matches played")
    wins: int = Field(0, description="Wins")
    losses: int = Field(0, description="Losses")
    draws: int = Field(0, description="Draws")
    user_id: int = Field(description="User ID that relates to the player")

    @field_validator("first_name")
    def validate_first_name(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("First name must contain only alphabetic characters")
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Last name must contain only alphabetic characters")
        return value

    @field_validator("country")
    def validate_country(cls, value: str) -> str:
        if len(value) < 2 or len(value) > 50:
            raise ValueError("Country must be between 2 and 50 characters")
        return value

    @field_validator("matches_played", "wins", "losses", "draws")
    def validate_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value


