from datetime import datetime

from pydantic import BaseModel, Field


class PicksBase(BaseModel):
    fight_id: int = Field(..., gt=0, description="Fight associated")
    winner_pick: int = Field(..., gt=0, description="Winner picked by the user")


# general model. also response model
class Picks(PicksBase):
    id: int = Field(..., gt=0, description="Pick id")
    created_at: datetime | None = Field(None, description="Set by the datebase (do not provide manually)", validate_default=True)

    class Config:
        from_attributes = True


class PicksCreate(PicksBase):
    pass
