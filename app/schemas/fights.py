from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.fighters import DivisionEnum


class RoundsEnum(int, Enum):
    three = 3
    five = 5


class WinningMethodEnum(str, Enum):
    decision = "Decision"
    ko = "KO"
    tko = "TKO"
    submission = "Submission"
    draw = "Draw"
    nc = "NC"
    dq = "DQ"


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


# post method
class FightsCreate(FightsBase):
    pass


# general model with full fields. also the returning model
class Fights(FightsBase):
    id: int = Field(..., gt=0, description="Unique fight id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
