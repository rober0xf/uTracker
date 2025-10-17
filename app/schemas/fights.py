from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date

from app.schemas.fighters import DivisionEnum


class RoundsEnum(int, Enum):
    three = 3
    five = 5


class WinningMethodEnum(str, Enum):
    decision = "decision"
    ko = "ko"
    tko = "tko"
    submission = "submission"
    draw = "draw"
    nc = "nc"
    dq = "dq"


# description creates a documentation, gt=0 enforces positive ids
class FightsBase(BaseModel):
    rounds: RoundsEnum = Field(..., description="Number of rounds (3 or 5)")
    division: DivisionEnum = Field(..., description="Weight class")
    method: WinningMethodEnum | None = Field(None, description="Winning method")
    card: int = Field(..., gt=0, description="Event card id")
    red_corner: int = Field(..., gt=0, description="Fighter id (red corner)")
    blue_corner: int = Field(..., gt=0, description="Fighter id (blue corner)")
    favorite: int | None = Field(None, gt=0, description="Fighter id that is favored in bettings")
    winner: int | None = Field(None, gt=0, description="Fighter id of the winner")
    round_finish: int | None = Field(None, gt=1, le=5, description="Round of the finish")
    fight_date: date = Field(..., description="format YY-MM-DD")


# post method
class FightsCreate(FightsBase):
    pass


# general model with full fields. also the returning model
class Fights(FightsBase):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    id: int = Field(..., gt=0, description="Unique fight id")
    created_at: datetime = Field(default_factory=datetime.now)


class FightsUpdate(BaseModel):
    """schema for put and patch request"""

    rounds: RoundsEnum | None = Field(None, ge=3, le=5)
    division: DivisionEnum | None = None
    method: WinningMethodEnum | None = Field(None, description="Winning method")
    card: int | None = None
    red_corner: int | None = Field(None, gt=0)
    blue_corner: int | None = Field(None, gt=0)
    favorite: int | None = None
    winner: int | None = None
    round_finish: int | None = Field(None)
    fight_date: str | None = None

    @field_validator("fight_date")
    @classmethod
    def validate_date(cls, v: str | None) -> date | None:
        if v is None:
            return None

        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("date must be in format %YYYY-%MM-%DD")
        if parsed_date > date.today():
            raise ValueError("fighter birth date cannot be in the future")
        return parsed_date


# post method
class FightForm(BaseModel):
    """schema for post request"""

    rounds: str
    division: str
    card_id: int
    red_corner: int
    blue_corner: int
    method: str | None = None
    favorite: int | None = None
    winner: int | None = None
    round_finish: int | None = None
    fight_date: str

    def to_fights_base_data(self) -> dict:
        """convert form strings to proper types for pydantic validation"""
        try:
            data = {
                "rounds": RoundsEnum(int(self.rounds)) if self.rounds else None,
                "division": DivisionEnum(self.division.strip()) if self.division else None,
                "card": int(self.card_id) if self.card_id else None,
                "red_corner": int(self.red_corner) if self.red_corner is not None and self.red_corner != "" else None,
                "blue_corner": int(self.blue_corner) if self.blue_corner is not None and self.blue_corner != "" else None,
                "method": WinningMethodEnum(self.method.strip()) if self.method else None,
                "favorite": int(self.favorite) if self.favorite is not None and self.favorite != "" else None,
                "winner": int(self.winner) if self.winner is not None and self.winner != "" else None,
                "round_finish": int(self.round_finish) if self.round_finish else None,
                "fight_date": date.fromisoformat(self.fight_date.strip()) if self.fight_date else None,
            }

            return data

        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid data conversion: {e}") from None
