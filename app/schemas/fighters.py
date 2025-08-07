from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


# use str as a parameter so it can be handled as a string
class DivisionEnum(str, Enum):
    flyweight = "flyweight"
    bantamweight = "bantamweight"
    featherweight = "featherweight"
    lightweight = "lightweight"
    welterweight = "welterweight"
    middleweight = "middleweight"
    light_heavyweight = "light_heavyweight"
    heavyweight = "heavyweight"


# description creates a documentation, gt=0 enforces positive ids
class FightersBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=50)
    division: DivisionEnum = Field(...)
    birth_date: date = Field(..., description="Fighter's date of birth, format YY-MM-DD")
    wins: int = Field(..., gt=0)
    losses: int = Field(..., ge=0)
    draws: int | None = Field(None)
    no_contest: int | None = Field(None)
    height: float = Field(gt=0, le=3.0, description="Height in meters (0 < x <= 3)")
    weight: float = Field(gt=0, le=120, description="Weight in kg (0 < x <= 120)")
    reach: int | None = Field(None, gt=0, le=225, description="Reach in cm (0 < x <= 225)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        name_len = len(name)
        if name_len < 5 or name_len > 50:
            raise ValueError(f"Fighter's name must be between 5-50 chars, current: {name_len}.")
        return name

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, t: date) -> date:
        if t > date.today():
            raise ValueError("Birth cannot be in the future hehe")
        return t

    @field_validator("wins", "losses")
    @classmethod
    def validate_record_stats(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Records should be positive")
        return value


# general schema. also the response model
class Fighters(FightersBase):
    model_config = ConfigDict(extra="ignore")

    id: int = Field(..., gt=0, description="Fighter id")
    created_at: datetime = Field(default_factory=datetime.now, description="When record was created")
    updated_at: datetime | None = Field(None, description="When stats were updated")


# post method
class FighterForm(BaseModel):
    """schema for post request"""

    name: str
    division: str
    birth_date: str
    wins: int
    losses: int
    draws: int | None = None
    no_contest: int | None = None
    height: float
    weight: float
    reach: float | None = None

    def to_fighters_base_data(self) -> dict:
        """convert form strings to proper types for pydantic validation"""
        try:
            data = {
                "name": self.name.strip() if self.name else "",
                "division": self.division.strip() if self.division else "",
                "birth_date": date.fromisoformat(self.birth_date.strip()) if self.birth_date else None,
                "wins": self.wins,
                "losses": self.losses,
                "height": self.height,
                "weight": self.weight,
                "draws": int(self.draws) if self.draws is not None or self.draws != "" else None,
                "no_contest": int(self.no_contest) if self.no_contest is not None or self.no_contest != "" else None,
                "reach": float(self.reach) if self.reach is not None or self.reach != "" else None,
            }

            return data

        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid data conversion: {e}") from None


class FightersUpdate(BaseModel):
    """schema for put and patch request"""

    name: str | None = Field(None, min_length=5, max_length=50)
    division: DivisionEnum | None = None
    birth_date: date | None = None
    wins: int | None = Field(None, gt=0)
    losses: int | None = Field(None, gt=0)
    draws: int | None = None
    no_contest: int | None = None
    height: float | None = Field(None, gt=0, le=3.0)
    weight: float | None = Field(None, gt=0, le=120)
    reach: float | None = Field(None, gt=0, le=225)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str | None) -> str | None:
        if name is None:
            return name

        name = name.strip()
        name_len = len(name)
        if name_len < 5 or name_len > 50:
            raise ValueError(f"the fighter name must be between 5-50 chars, current: {name_len}.")
        return name

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, birth_date: date | None) -> date | None:
        if birth_date is None:
            return birth_date

        if birth_date > date.today():
            raise ValueError("fighter birth date cannot be in the future")
        return birth_date
