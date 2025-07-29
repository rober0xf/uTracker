from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, field_validator

# handle if empty card number, convert "" to null
card_number_type = Annotated[int | None, BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v)]


class CardsBase(BaseModel):
    card_name: str = Field(..., min_length=5, max_length=50, description="Name of the card (5-50 chars)")
    card_date: date = Field(..., description="Scheduled date")
    card_number: card_number_type = Field(None, description="Optional card number if its numerated", gt=0)

    @field_validator("card_name")
    def validate_card_name(cls, name: str) -> str:
        name = name.strip()  # clean the whitespaces
        name_len = len(name)
        if not (5 <= name_len <= 50):
            raise ValueError(f"the card name must be between 5 and 50 chars long, current: {name_len}.")
        return name

    @field_validator("card_date")
    def validate_card_date(cls, t: date) -> date:
        if t < date.today():
            raise ValueError("Card date cannot be in the past")
        return t

    @field_validator("card_number")
    def validate_card_number(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Card number must be positive if its numerated")
        return v


class CardsCreate(CardsBase):
    pass


class Cards(CardsBase):
    id: int = Field(..., gt=0)
    created_at: datetime | None = Field(None, description="Set by the datebase (do not provide manually)", validate_default=True)

    class Config:
        from_attributes = True
