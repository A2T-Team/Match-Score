from datetime import datetime, timedelta
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional
import uuid

class CreateMatchRequest(BaseModel):
    format: str = Field(examples=["Format must be 'time' or 'score'"])
    end_condition: int = Field(description="Minutes for 'time' format or points for 'score' format")
    player_a: uuid.UUID = Field(description="First player ID")
    player_b: uuid.UUID = Field(description="Second player ID")
    start_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    end_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    prize: Optional[int] = Field(description="Prize for the match, must be 0 or positive")
    #author_id: uuid.UUID = Field(description="Author ID")
    tournament_id: Optional[uuid.UUID] = Field(description="Tournament ID")
    stage: Optional[int] = Field(description="Stage if in tournament")
    serial_number: Optional[int] = Field(description="Serial number if in tournament")

    @field_validator("format", mode="before")
    def validate_format(cls, value, info: FieldValidationInfo):
        tournament_id = info.data.get("tournament_id")
        if tournament_id and value:
            raise ValueError("Format should not be specified manually if the match is part of a tournament.")
        if not tournament_id and value not in ["time", "score"]:
            raise ValueError("Match format must be 'time' or 'score' for non-tournament matches.")
        return value

    @field_validator("prize", mode="before")
    def validate_prize(cls, value, info: FieldValidationInfo):
        tournament_id = info.data.get("tournament_id")
        if value == "":
            return None
        if tournament_id and value is not None:
            raise ValueError("Prize should not be specified manually if the match is part of a tournament.")
        if value is not None and value < 0:
            raise ValueError("Prize must be 0 or positive")
        return value

    @field_validator("end_condition")
    def validate_end_condition(cls, value, info: FieldValidationInfo):
        match_format = info.data.get("format")
        if match_format == "time" and value <= 0:
            raise ValueError("For 'time' format, end_condition must be positive (minutes).")
        if match_format == "score" and value <= 0:
            raise ValueError("For 'score' format, end_condition must be positive (points).")
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

        match_format = info.data.get("format")
        start_time = info.data.get("start_time")
        end_condition = info.data.get("end_condition")

        if match_format == "time" and start_time:
            return start_time + timedelta(minutes=end_condition)
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
    
    @field_validator("stage", "serial_number", "tournament_id", mode="before")
    def validate_stage_serial_number(cls, value):
        if value == "":
            return None
        return value
# class MatchUpdate(BaseModel):
#     score_a: Optional[int] = None
#     score_b: Optional[int] = None
#     result_code: Optional[str] = None
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     prize: Optional[int] = None

class MatchResult(BaseModel):
    score_a: int = Field(description="Score for Player A")
    score_b: int = Field(description="Score for Player B")
    result_code: str = Field(description="Result code for the match")


    @field_validator("score_a", "score_b")
    def validate_score(cls, value):
        if value < 0:
            raise ValueError("Score must be above 0")
        return value

    @field_validator("result_code")
    def validate_result_code(cls, value):
        if value not in ["player 1", "player 2", "draw"]:
            raise ValueError("Result must be 'player 1', 'player 2', or 'draw'")
        return value

class MatchUpdateTime(BaseModel):
    start_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"], description="Updated match start time")
    end_time: Optional[datetime] = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"], description="Updated match end time")

    @field_validator("start_time", mode="before")
    def validate_start_time(cls, value):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, r"%Y/%m/%d %H:%M")
            except ValueError:
                raise ValueError("Expected format is 'YYYY/MM/DD HH:MM'")
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
        return value


class MatchResponse(CreateMatchRequest):
    id: uuid.UUID
    format: str
    end_condition: int
    player_a: uuid.UUID
    player_b: uuid.UUID
    start_time: datetime
    end_time: datetime
    prize: Optional[int]
    author_id: uuid.UUID
    tournament_id: Optional[uuid.UUID]
    stage: Optional[int]
    serial_number: Optional[int]

    # model_config = {
    #     "from_attributes": True,  # Enables ORM mode
    # }