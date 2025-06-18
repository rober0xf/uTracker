from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.fighters import DivisionEnum


class RoundsEnum(str, Enum):
    three = "three"
    five = "five"


class WinningMethodEnum(str, Enum):
    KO = "KO"
    TKO = "TKO"
    submission = "Submission"
    draw = "Draw"
    NC = "NC"
    DQ = "DQ"
    decision = "Decision"


# description creates a documentation, gt=0 enforces positive ids
class FightsBase(BaseModel):
    rounds: RoundsEnum = Field(..., description="Number of rounds (3 or 5)")
    division: DivisionEnum = Field(..., description="Weight class")
    method: WinningMethodEnum = Field(..., description="Winning method")
    card: int = Field(..., gt=0, description="Event card id")
    red_corner: int = Field(..., gt=0, description="Fighter id (red corner)")
    blue_corner: int = Field(..., gt=0, description="Fighter id (blue corner)")
    favorite: Optional[int] = Field(
        None, gt=0, description="Fighter id that is favored in bettings"
    )
    winner: Optional[int] = Field(None, gt=0, description="Fighter id of the winner")
    round_finish: Optional[int] = Field(
        None, gt=1, le=5, description="Round of the finish"
    )


# general model with full fields. also the returning model
class Fights(FightsBase):
    id: int = Field(..., gt=0, description="Unique fight id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


# post method
class FightsCreate(FightsBase):
    pass


class FightsUpdate(BaseModel):
    rounds: RoundsEnum | None = None
    division: DivisionEnum | None = None
    method: WinningMethodEnum | None = None
    card: int | None = Field(None, gt=0)
    red_corner: int | None = Field(None, gt=0)
    blue_corner: int | None = Field(None, gt=0)
    favorite: int | None = Field(None, gt=0)
    winner: int | None = Field(None, gt=0)
    round_finish: int | None = Field(None, gt=1, le=5)


class FightsPatch(FightsUpdate):
    pass
