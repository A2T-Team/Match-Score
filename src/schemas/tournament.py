from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateTournamentRequest(BaseModel):
    name: str = Field(
        min_length=5,
        max_length=45,
        examples=["Black Doll Winter 2024"]
    )
    tournament_format: str = Field(
        examples=["Format must be 'league' or 'knockout'"]
    )
    match_format: str = Field(
        examples=["Format must be 'time' or 'score'"] # names are suggestion
    )
    start_date: datetime = Field(
        examples=["Format must be 'YYYY/MM/DD HH:MM"]
    )
    end_date: datetime = Field(
        examples=["Format must be 'YYYY/MM/DD HH:MM"]
    )
    prize: int = Field(ge=0, description="Prize for the tournament, must be 0 or positive")


    @field_validator("tournament_format")
    def validate_tournament_format(cls, value):
        if value not in ["league", "knockout"]:
            raise ValueError("Tournament format must be 'league' or 'knockout'")
        return value
    
    
    @field_validator("match_format")
    def validate_match_format(cls, value):
        if value not in ["time", "score"]:
            raise ValueError("Match format must be 'time' or 'score'")
        return value
    

    @field_validator('start_date', mode='before')
    def validate_start_date(cls, value):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y/%m/%d %H:%M") 
            except ValueError:
                raise ValueError("Expected format is 'YYYY/MM/DD HH:MM'")
        if value < datetime.now():
            raise ValueError("Start date cannot be in the past.")
        return value
    

    @field_validator('end_date', mode='before')
    def validate_end_date(cls, value, values):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y/%m/%d %H:%M") 
            except ValueError:
                raise ValueError("Expected format is 'YYYY/MM/DD HH:MM'")
            
        start_date = values.get('start_date')
        # values is a dictionary that contains all the previously validated field values 
        # of the model up to that point.
       
        if start_date and value < start_date:
            raise ValueError("End date cannot be before the start date.")
        if value < datetime.now():
            raise ValueError("End date cannot be in the past.")
        
        return value
    
