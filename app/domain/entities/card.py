from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Card:
    id: int | None
    card_name: str
    card_date: date
    card_number: int | None
    created_at: datetime | None = None

    def __post_init__(self):
        self.card_name = self.card_name.strip()

        if len(self.card_name) < 6 or len(self.card_name) > 100:
            raise ValueError("card name cannot be less than 6 chars or greather than 100 chars")

        if self.card_number is not None and self.card_number <= 0:
            raise ValueError("card number must be positive")

    def check_future_date(self):
        if self.card_date < date.today():
            raise ValueError("card cannot be in the past")
