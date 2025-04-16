from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Cards(BaseModel):
    id: int = Field(..., gt=0, description='Card id')
    card_name: str = Field(..., min_length=5, max_length=50, description='Name of the card (5-50 chars)')
    card_date: datetime = Field(..., description='Scheduled date')
    main_event_id: int = Field(..., gt=0, description='ID from the main event fight')
    created_at: Optional[datetime] = Field(None, description='Set by the datebase (do not provide manually)', validate_default=True)

    @field_validator('card_name')
    def validate_card_name(cls, name: str) -> str:
        name = name.strip()  # clean the whitespaces
        name_len = len(name)
        if not (5 <= name_len <= 50):
            raise ValueError(f'the card name must be between 5 and 50 chars long, current: {name_len}.')
        return name

    @field_validator('card_date')
    def validate_card_date(cls, t: datetime) -> datetime:
        if t < datetime.now():
            raise ValueError('Card date cannot be in the past')
        return t
