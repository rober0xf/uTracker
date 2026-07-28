from dataclasses import dataclass
from datetime import date

from app.domain.enums.enums import DivisionEnum


@dataclass
class Fighter:
    id: int | None
    name: str
    division: DivisionEnum
    birth_date: date
    height: float
    weight: float
    wins: int = 0
    losses: int = 0
    draws: int = 0
    no_contest: int = 0
    reach: float | None = None

    def __post_init__(self):
        self.name = self.name.strip()

        if not self.name:
            raise ValueError("fighter name cannot be empty")
        if len(self.name) > 100:
            raise ValueError("fighter name cannot be longer than 100 chars")
        if self.birth_date >= date.today():
            raise ValueError("birth date must be in the past")
        if self.height <= 0:
            raise ValueError("height must be positive")
        if self.weight <= 0:
            raise ValueError("weight must be positive")
        if self.reach is not None and self.reach <= 0:
            raise ValueError("reach must be positive")

        for v in (self.wins, self.losses, self.draws, self.no_contest):
            if v < 0:
                raise ValueError("record value cannot be negative")
