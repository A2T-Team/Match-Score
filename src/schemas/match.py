from datetime import datetime
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional
import uuid


class CreateMatchRequest(BaseModel):
    #name: str = Field(min_length=5, max_length=50, examples=["Black Doll Winter 2024"])
    format: str = Field(examples=["Format must be 'time' or 'score'"])
    # match_format: str = Field(
    #     examples=["Format must be 'time' or 'score'"]  # names are suggestion
    # )
    player_a: int = Field(description=["First player ID"])
    player_b: int = Field(description=["Second player ID"])
    score_a: int = Field(ge=0, examples=["Score must be 0 or positive"])
    score_b: int = Field(ge=0, examples=["Score must be 0 or positive"])
    result_code: str = Field(examples=["Result must be 'player 1' , 'player 2' or 'draw'"])
    start_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM"])
    end_time: datetime = Field(examples=["Format must be 'YYYY/MM/DD HH:MM'"])
    prize: int = Field(
        ge=0, description="Prize for the match, must be 0 or positive"
    )
    author_id: uuid.UUID = Field(
        description="Author ID"
    )
    tournament_id: int = Field(description=["Tournament ID"])

    @field_validator("format")
    def validate_format(cls, value):
        if value not in ["time", "score"]:
            raise ValueError("Match format must be 'time' or 'score'")
        return value

    @field_validator("result_code")
    def validate_match_format(cls, value):
        if value not in ["player 1", "player 2", "draw"]:
            raise ValueError("Result format must be 'player 1' , 'player 2' or 'draw'")
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
