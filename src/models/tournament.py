from models.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func


class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(UUID(as_uuid=True), 
                primary_key=True, 
                default=uuid.uuid4,
                unique=True,
                nullable=False,)
    name = Column(String,
                  unique=True,
                  nullable=False)
    tournament_format = Column(String,
                               index=True,
                               nullable=False)
    match_format = Column(String,
                          nullable=False)
    start_date = Column(DateTime, 
                        nullable=False)
    end_date = Column(DateTime,
                      nullable=False)
    prize = Column(Integer, 
                   nullable=False)
    matches = relationship("Match", back_populates="tournament") # Add in class Match - tournament = relationship("Tournament", back_populates="matches")
    participants = relationship("Participant", back_populates="tournament") # Add in class Participant - tournament = relationship("Tournament", back_populates="participants")
    winner = Column(UUID(as_uuid=True), 
                    ForeignKey("participants.id"), 
                    nullable=True)
    

    @validates("tournament_format", "match_format")
    def validate_fields(self, key, value):
        if key == "tournament_format" and value not in ["league", "knockout"]:
            raise ValueError("Tournament format must be 'league' or 'knockout'")
        if key == "match_format" and value not in ["time", "score"]: # Assumption for the names
            raise ValueError("Match format must be 'time' or 'score'")
        return value
    
    
    def __repr__(self):
        return f"Tournament '{self.name}', start date '{self.start_date}', end date '{self.end_date}')"