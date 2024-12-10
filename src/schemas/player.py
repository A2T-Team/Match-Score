from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
import re


class CreatePlayerRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50, examples=["John"], description="Player's first name, between 2 and 50 characters")
    last_name: str = Field(min_length=2, max_length=50, examples=["Doe"], description="Player's last name, between 2 and 50 characters")
    country: Optional[str] = Field(min_length=2, max_length=50, examples=["Bulgaria"], description="For which country the player competes")
    team_id: Optional[UUID] = Field(examples=['7e3d1be2-2f6f-4bb3-91a5-2f6157a3f089'], description="UUID of the team the player belongs to")
    # matches_played: int = Field(0, description="Matches played")
    # wins: int = Field(0, description="Wins")
    # losses: int = Field(0, description="Losses")
    # draws: int = Field(0, description="Draws")
    # points: int = Field(0, description="Points")
    user_id: Optional[UUID] = Field(examples=['7e3d1be2-2f6f-4bb3-91a5-2f6157a3f089'], description="User ID that relates to the player")

    @field_validator("first_name")
    def validate_first_name(cls, value: str) -> str:
        if not re.match(r"^[A-Za-z\s\-]+$", value):
            raise ValueError("First name must contain only alphabetic characters, dashes, or spaces")
        return value

    @field_validator("last_name")
    def validate_last_name(cls, value: str) -> str:
        if not re.match(r"^[A-Za-z \-']+$", value):
            raise ValueError("Last name must contain only alphabetic characters, dashes, spaces, or apostrophes")
        return value

    @field_validator("country")
    def validate_country(cls, value: str) -> str:
        if value is None:
            return ''
        if not value.isalpha():
            raise ValueError("Country must contain only alphabetic characters")
        return value
    
    @field_validator("team_id", "user_id", mode="before")
    def handle_empty_strings(cls, value):
        if value == "":
            return None
        return value
    # @field_validator("matches_played", "wins", "losses", "draws", "points")
    # def validate_non_negative(cls, value: int) -> int:
    #     if value < 0:
    #         raise ValueError("Value must be non-negative")
    #     return value


class PlayerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country: Optional[str] = None
    #team_id: Optional[UUID] = None

# class PlayerWithUser(BaseModel):
#     user_id: UUID = Field(
#         description="UUID of the user associated with the player",
#         examples=['7e3d1be2-2f6f-4bb3-91a5-2f6157a3f089']
#     )



class PlayerResponse(CreatePlayerRequest):
    id: Optional[UUID]
    first_name: str
    last_name: str
    country: Optional[str] = None
    team_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    wins: int
    losses: int
    draws: int

class ParticipantResponse(CreatePlayerRequest):
    first_name: str
    last_name: str
    country: Optional[str] = None
    team_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    wins: int
    losses: int
    draws: int
    stage: Optional[int] = None
    serial_number: Optional[int] = None




    # model_config = {
    #     "from_attributes": True,  # Enables ORM mode
    # }