from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator

# handle if empty card number, convert "" to null
card_number_type = Annotated[
    int | None,
    BeforeValidator(lambda v: None if isinstance(v, str) and v.strip() == "" else v),
]


# base schema. no date validation
class CardsBase(BaseModel):
    card_name: str = Field(..., min_length=5, max_length=50, description="name of the card (5-50 chars)")
    card_date: date = Field(..., description="scheduled date")
    card_number: card_number_type | None = Field(None)

    @field_validator("card_name")
    @classmethod
    def validate_card_name(cls, name: str) -> str:
        return name.strip()

    @field_validator("card_number", mode="before")
    @classmethod
    def validate_card_number(cls, v: Any) -> int | None:
        if v in ("", "None", "null", None):
            return None
        if isinstance(v, str):
            try:
                v = int(v.strip())
            except ValueError:
                raise ValueError("card_number must be an integer") from None

        # Validate positive number only if not None
        if v is not None and v <= 0:
            raise ValueError("card_number must be positive")

        return v


# for post method. validate date format and future creation card
class CardsCreate(CardsBase):
    @field_validator("card_date", mode="before")
    @classmethod
    def parse_and_validate_date(cls, v: Any):
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except ValueError:
                raise ValueError("invalid date format, should be: %Y-%m-%d") from None
        return v

    @field_validator("card_date")
    @classmethod
    def validate_future_date(cls, v: date):
        if v < date.today():
            raise ValueError("card cannot be in the past")
        return v

    @classmethod
    def parse_number_field(cls, string_card_number: str | int | None) -> int | None:
        if isinstance(string_card_number, str):
            parsed_card_number = int(string_card_number) if string_card_number and string_card_number.strip() else None
        elif string_card_number is None:
            return None
        else:
            parsed_card_number = string_card_number

        return parsed_card_number


class CardForm(BaseModel):
    card_name: str
    card_date: str
    card_number: int | None = None

    def to_cards_base_data(self) -> dict:
        """convert form strings to proper types for pydantic validation"""
        try:
            data = {
                "card_name": self.card_name.strip() if self.card_name else "",
                "card_date": date.fromisoformat(self.card_date.strip()) if self.card_date else None,
                "card_number": int(self.card_number) if self.card_number else None,
            }

            return data

        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid data conversion: {e}") from None


class CardsResponse(CardsBase):
    pass


class Cards(CardsBase):
    model_config = ConfigDict(extra="ignore", from_attributes=True)
    id: int = Field(..., gt=0)
    created_at: datetime | None = Field(
        None,
        description="Set by the datebase (do not provide manually)",
        validate_default=True,
    )
