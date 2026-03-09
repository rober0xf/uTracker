from dataclasses import dataclass
from datetime import date

from enums.enums import DivisionEnum, RoundsEnum


@dataclass
class Fight:
    id: int | None
    rounds: RoundsEnum
    division: DivisionEnum
    card_id: int
    fight_date: date
    red_corner_id: int
    blue_corner_id: int
    favorite_fighter_id: int | None = None
    winner_id: int | None = None
    round_finish: int | None = None

    def __post_init__(self):
        if self.red_corner_id == self.blue_corner_id:
            raise ValueError("a fighter cannot fight with himself")

        if (
            self.round_finish is not None
            and self.round_finish <= 0
            or self.round_finish is not None
            and self.round_finish > 5
        ):
            raise ValueError("round finish must be between 1-5")

    def set_winner(self, fighter_id: int, round_finish: int | None = None):
        if fighter_id not in (self.red_corner_id, self.blue_corner_id):
            raise ValueError("winner is not between fighters")

        self.winner_id = fighter_id
        self.round_finish = round_finish

    def check_future_date(self):
        if self.fight_date < date.today():
            raise ValueError("fight cannot be in the past")
