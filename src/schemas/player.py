from datetime import datetime
from pydantic import BaseModel, Field, field_validator, FieldValidationInfo
from typing import Optional
import uuid


class CreatePlayerRequest(BaseModel):
    
    first_name: str = Field(min_length=2 , max_length=50 , examples=["John"])
    last_name: str = Field(min_length=2 , max_length=50 , examples=["Doe"])
    country: str = Field(description=["For which country the player competes"])
    team_id: int = Field(description=["Player's team"])
    matches_played: int = Field(description=["Matches played"])
    wins: int = Field(description=["Wins"])
    losses: int = Field(description=["Losses"])
    draws: int = Field(description=["Draws"])
    user_id: int = Field(description=["User ID that relates to the player"])
    


