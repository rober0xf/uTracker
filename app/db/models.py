from datetime import date, datetime
from typing import override

from sqlalchemy import CheckConstraint, Date, Enum, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from app.schemas.fighters import DivisionEnum
from app.schemas.fights import RoundsEnum, WinningMethodEnum

from .features import FighterFeatures


class Base(DeclarativeBase):
    pass


class FightersDB(Base):
    __tablename__: str = "fighters"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    no_contest: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    reach: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # created when the record its created
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)

    # constraints
    __table_args__: tuple[CheckConstraint, ...] = (
        CheckConstraint("LENGTH(name) >= 5", name="name_min_length"),
        CheckConstraint("LENGTH(name) <=50", name="name_max_length"),
    )

    features: Mapped["FighterFeatures"] = relationship("FighterFeatures", back_populates="fighter", uselist=False)


class FightsDB(Base):
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
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    red_fighter: Mapped["FightersDB"] = relationship("FightersDB", foreign_keys=[red_corner])
    blue_fighter: Mapped["FightersDB"] = relationship("FightersDB", foreign_keys=[blue_corner])
    favorite_fighter: Mapped["FightersDB"] = relationship("FightersDB", foreign_keys=[favorite])
    winner_fighter: Mapped["FightersDB"] = relationship("FightersDB", foreign_keys=[winner])

    @override
    def __repr__(self):
        return f"<Fight(id={self.id}, red={self.red_corner}, blue={self.blue_corner})>"


class CardsDB(Base):
    __tablename__: str = "cards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    card_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    card_number: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # constraints
    __table_args__: tuple[CheckConstraint, ...] = (
        CheckConstraint("LENGTH(card_name) >= 5", name="card_name_min_length"),
        CheckConstraint("LENGTH(card_name) <=50", name="card_name_max_length"),
    )


class PicksDB(Base):
    __tablename__: str = "picks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fight_id: Mapped[int] = mapped_column(ForeignKey("fights.id"), nullable=False)
    winner_pick: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    fight: Mapped["FightsDB"] = relationship("FightsDB", foreign_keys=[fight_id])
    winner_picked: Mapped["FightsDB"] = relationship("FightersDB", foreign_keys=[winner_pick])
