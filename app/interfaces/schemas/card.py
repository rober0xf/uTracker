from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

# handle if empty card number, convert "" to null
card_number_type = Annotated[
    int | None,
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v),
]


# base schema. no date validation
class CardBase(BaseModel):
    card_name: str = Field(..., min_length=5, max_length=50)
    card_date: date
    card_number: card_number_type = None

    @field_validator("card_name")
    @classmethod
    def validate_card_name(cls, name: str) -> str:
        return name.strip()

    @field_validator("card_number", mode="before")
    @classmethod
    def validate_card_number(cls, v: int | None):
        if v is not None and v <= 0:
            raise ValueError("card_number must be positive")

        return v


# for post method. validate date format and future creation card
class CardCreate(CardBase):
    @field_validator("card_date")
    @classmethod
    def validate_future_date(cls, v: date):
        if v < date.today():
            raise ValueError("card cannot be in the past")
        return v


# response api
class CardRead(CardBase):
    id: int
    created_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
