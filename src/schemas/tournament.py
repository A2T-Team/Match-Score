from datetime import datetime
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional, List
import uuid


class CreateTournamentRequest(BaseModel):
    name: str = Field(min_length=5, max_length=50, examples=["Black Doll Winter 2024"])
    format: str = Field(examples=["Format must be 'league' or 'knockout'"])
    match_format: str = Field(
        examples=["Format must be 'time' or 'score'"]  # names are suggestion
    )
    start_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM"])
    end_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    prize: int = Field(
        ge=0, description="Prize for the tournament, must be 0 or positive"
    )
    win_points: int = Field(
        ge=0, description="How many points the winner gets"
    )
    draw_points: int = Field(
        ge=0, description="How many points the players get on draw"
    )
    author_id: uuid.UUID = Field(
        description="Author ID"
    )

    @field_validator("format")
    def validate_format(cls, value):
        if value not in ["league", "knockout"]:
            raise ValueError("Tournament format must be 'league' or 'knockout'")
        return value

    @field_validator("match_format")
    def validate_match_format(cls, value):
        if value not in ["time", "score"]:
            raise ValueError("Match format must be 'time' or 'score'")
        return value

    @field_validator("start_time", mode="before")
    def validate_start_time(cls, value):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, r"%Y/%m/%d %H:%M")
            except ValueError:
                raise ValueError("Expected format is 'YYYY/MM/DD HH:MM'")
        if value < datetime.now():
            raise ValueError("Start date cannot be in the past.")
        return value

    @field_validator("end_time", mode="before")
    def validate_end_time(cls, value, info: FieldValidationInfo):
        # info.data is a dictionary that contains all the previously validated field values
        # of the model up to that point.
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, r"%Y/%m/%d %H:%M")
            except ValueError:
                raise ValueError("Expected format is 'YYYY/MM/DD HH:MM'")

        start_time = info.data.get("start_time")

        if start_time and value < start_time:
            raise ValueError("End date cannot be before the start date.")
        if value < datetime.now():
            raise ValueError("End date cannot be in the past.")

        return value


class AddAllTournamentParticipants(BaseModel):
    participants: List[str] = Field(description="List of all participants", example=["player1_full_name", "player2_full_name"])


class UpdateSingleMatchInTournament(BaseModel):
    tournament_id: uuid.UUID = Field(description="Tournament ID")
    match_id: uuid.UUID = Field(description="Match ID")
    participants: List[str] = Field(description="List of all participants", example=["player1_full_name", "player2_full_name"])

class UpdateTournament(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None