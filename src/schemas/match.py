from datetime import datetime
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional
import uuid

class CreateMatchRequest(BaseModel):
    format: str = Field(examples=["Format must be 'time' or 'score'"])
    end_condition: int = Field(description=["Minutes for 'time' format or points for 'score' format"])
    player_a: uuid.UUID = Field(description="First player ID")
    player_b: uuid.UUID = Field(description="Second player ID")
    score_a: int = Field(ge=0, examples=["Score must be 0 or positive"])
    score_b: int = Field(ge=0, examples=["Score must be 0 or positive"])
    result_code: str = Field(examples=["Result must be 'player 1', 'player 2', or 'draw'"])
    start_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    end_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    prize: int = Field(ge=0, description="Prize for the match, must be 0 or positive")
    author_id: uuid.UUID = Field(description="Author ID")
    tournament_id: uuid.UUID = Field(description="Tournament ID")

    @field_validator("format")
    def validate_format(cls, value):
        if value not in ["time", "score"]:
            raise ValueError("Match format must be 'time' or 'score'")
        return value
    
    @field_validator("end_condition")
    def validate_non_negative(cls, value):
        if value < 0:
            raise ValueError("Value must be non-negative")
        return value

    @field_validator("result_code")
    def validate_result_code(cls, value):
        if value not in ["player 1", "player 2", "draw"]:
            raise ValueError("Result must be 'player 1', 'player 2', or 'draw'")
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

    @field_validator("player_b")
    def validate_different_players(cls, player_b, info: FieldValidationInfo):
        player_a = info.data.get("player_a")
        if player_a and player_b == player_a:
            raise ValueError("Player A and Player B cannot be the same.")
        return player_b

class MatchUpdate(BaseModel):
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    result_code: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    prize: Optional[int] = None

class MatchResponse(CreateMatchRequest):
    id: uuid.UUID = Field(..., description="Unique ID of the match")

    model_config = {
        "from_attributes": True,  # Enables ORM mode
    }