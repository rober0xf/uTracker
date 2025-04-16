from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, field_validator, Field


# use str as a parameter so it can be handled as a string
class DivisionEnum(str, Enum):
    flyweight = 'flyweight'
    bantamweight = 'bantamweight'
    featherweight = 'featherweight'
    lightweight = 'lightweight'
    welterweight = 'welterweight'
    middleweight = 'middleweight'
    light_heavyweight = 'light_heavyweight'
    heavyweight = 'heavyweight'


# description creates a documentation, gt=0 enforces positive ids
class Fighters(BaseModel):
    id: int = Field(..., gt=0, description='Fighter id')
    name: str = Field(..., min_length=5, max_length=50, description="Fighter's name")
    division: DivisionEnum = Field(..., description='Division where fights')
    birth_date: datetime = Field(..., description="Fighter's date of birth")
    wins: int = Field(..., gt=0, description='Amount of wins from the record')
    losses: int = Field(..., gt=0, description='Amount of losses from the record')
    draws: Optional[int] = Field(None, description='Amount of draws from the record')
    no_contest: Optional[int] = Field(None, description='Amount of no contest from the record')
    height: Optional[float] = Field(None, gt=0, le=3.0, description='Height in meters (0 < x <= 3)')
    weight: Optional[float] = Field(None, gt=0, le=120, description='Weight in kg (0 < x <= 120)')
    reach: Optional[float] = Field(None, gt=0, le=225, description='Reach in cm (0 < x <= 225)')
    created_at: datetime = Field(default_factory=datetime.now, description='When record was created')
    updated_at: Optional[datetime] = Field(None, description='When stats were updated')

    @field_validator('name')
    def validate_name(cls, name: str) -> str:
        name_len = len(name)
        if name_len < 5 or name_len > 50:
            raise ValueError(f"Fighter's name must be between 5-50 chars, current: {name_len}.")
        return name

    @field_validator('birth_date')
    def validate_birth_date(cls, t: datetime) -> datetime:
        if t > datetime.now():
            raise ValueError('Birth cannot be in the future hehe')
        return t
