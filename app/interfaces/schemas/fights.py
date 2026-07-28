from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.enums import DivisionEnum, RoundsEnum, WinningMethodEnum


class FightBase(BaseModel):
    rounds: RoundsEnum
    division: DivisionEnum
    method: WinningMethodEnum | None = None
    card_id: int = Field(..., gt=0)
    red_corner_id: int = Field(..., gt=0)
    blue_corner_id: int = Field(..., gt=0)
    favorite_fighter_id: int | None = Field(None, gt=0)
    winner_id: int | None = Field(None, gt=0)
    round_finish: int | None = Field(None, gt=1, le=5)
    fight_date: date


class FightRead(FightBase):
    id: int = Field(..., gt=0)
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# annotated is for keep quiet basedpyright
class FightUpdate(BaseModel):
    rounds: RoundsEnum | None = None
    division: DivisionEnum | None = None
    method: WinningMethodEnum | None = None
    card_id: Annotated[int | None, Field(gt=0)] = None
    red_corner_id: Annotated[int | None, Field(gt=0)] = None
    blue_corner_id: Annotated[int | None, Field(gt=0)] = None
    favorite_fighter_id: Annotated[int | None, Field(gt=0)] = None
    winner_id: Annotated[int | None, Field(gt=0)] = None
    round_finish: Annotated[int | None, Field(gt=0, le=5)] = None
    fight_date: date | None = None


class FightForm(BaseModel):
    rounds: str
    division: str
    method: str | None
    card: str
    red_corner: int
    blue_corner: int
    favorite: str
    winner: str
    round_finish: str | None
    fight_date: str

    def to_fights_base_data(self):
        return {
            "rounds": RoundsEnum(int(self.rounds)),
            "division": DivisionEnum(self.division),
            "method": WinningMethodEnum(self.method) if self.method else None,
            "card": int(self.card),
            "red_corner": int(self.red_corner),
            "blue_corner": int(self.blue_corner),
            "favorite": int(self.favorite),
            "winner": int(self.winner),
            "round_finish": int(self.round_finish) if self.round_finish else None,
            "fight_date": self.fight_date,
        }


class FightUpdateForm(BaseModel):
    fight_date: str | None = None
    rounds: int | None = None
    division: str | None = None
    method: str | None = None
    card: int | None = None
    red_corner: int | None = None
    blue_corner: int | None = None
    favorite: int | None = None
    winner: int | None = None
    round_finish: int | None = None
