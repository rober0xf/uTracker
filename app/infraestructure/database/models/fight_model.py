from datetime import date, datetime
from typing import override

from domain.enums.enums import DivisionEnum, RoundsEnum, WinningMethodEnum
from sqlalchemy import Date, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from .base_model import Base
from .fighter_model import FighterDB


class FightDB(Base):
    __tablename__: str = "fights"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rounds: Mapped[RoundsEnum] = mapped_column(Enum(RoundsEnum), nullable=False)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    method: Mapped[WinningMethodEnum | None] = mapped_column(Enum(WinningMethodEnum), nullable=True)
    card: Mapped[int] = mapped_column(ForeignKey("cards.id"), nullable=False)
    red_corner: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    blue_corner: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    favorite: Mapped[int | None] = mapped_column(ForeignKey("fighters.id"), nullable=True)
    winner: Mapped[int | None] = mapped_column(ForeignKey("fighters.id"), nullable=True)
    round_finish: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fight_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    red_fighter: Mapped["FighterDB"] = relationship("FightersDB", foreign_keys=[red_corner])
    blue_fighter: Mapped["FighterDB"] = relationship("FightersDB", foreign_keys=[blue_corner])
    favorite_fighter: Mapped["FighterDB"] = relationship("FightersDB", foreign_keys=[favorite])
    winner_fighter: Mapped["FighterDB"] = relationship("FightersDB", foreign_keys=[winner])

    @override
    def __repr__(self):
        return f"<Fight(id={self.id}, red={self.red_corner}, blue={self.blue_corner})>"
