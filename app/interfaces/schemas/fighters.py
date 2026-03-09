from datetime import date, datetime

from domain.enums.enums import DivisionEnum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class FighterBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=50)
    division: DivisionEnum
    birth_date: date
    wins: int = Field(..., ge=0)
    losses: int = Field(..., ge=0)
    draws: int | None = Field(0, ge=0)
    no_contest: int | None = Field(0, ge=0)
    height: float = Field(..., gt=0, le=3.0)
    weight: float = Field(..., gt=0, le=120)
    reach: float | None = Field(None, gt=0, le=225)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, t: date) -> date:
        if t > date.today():
            raise ValueError("birth date cannot be in the future")
        return t


class FighterRead(FighterBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class FighterUpdate(BaseModel):
    name: str | None = Field(None, min_length=5, max_length=50)
    division: DivisionEnum | None = None
    birth_date: date | None = None
    wins: int | None = Field(None, ge=0)
    losses: int | None = Field(None, ge=0)
    draws: int | None = Field(None, ge=0)
    no_contest: int | None = Field(None, ge=0)
    height: float | None = Field(None, gt=0, le=3.0)
    weight: float | None = Field(None, gt=0, le=120)
    reach: float | None = Field(None, gt=0, le=225)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None):
        if v is None:
            return v
        return v.strip()

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, t: date | None):
        if t is None:
            return t
        if t > date.today():
            raise ValueError("birth date cannot be in the future")
        return t


class FighterForm(BaseModel):
    name: str
    division: str
    birth_date: date
    wins: int
    losses: int
    draws: int | None = None
    no_contest: int | None = None
    height: float
    weight: float
    reach: float | None = None

    def to_fighter_base_data(self) -> dict:
        return {
            "name": self.name,
            "division": DivisionEnum(self.division),
            "birth_date": self.birth_date,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "no_contest": self.no_contest,
            "height": self.height,
            "weight": self.weight,
            "reach": self.reach,
        }
