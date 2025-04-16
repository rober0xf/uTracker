from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Picks(BaseModel):
    id: int = Field(..., gt=0, description='Pick id')
    fight_id: int = Field(..., gt=0, description='Fight associated')
    winner_pick: int = Field(..., gt=0, description='Winner picked by the user')
    created_at: Optional[datetime] = Field(None, description='Set by the datebase (do not provide manually)', validate_default=True)
