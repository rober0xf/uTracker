from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, Enum, Integer, String, Date
from app.schemas.fights import RoundsEnum, WinningMethodEnum
from app.schemas.fighters import DivisionEnum
from sqlalchemy.sql.schema import ForeignKey
from datetime import date, datetime
from sqlalchemy.sql import func
from typing import Optional


Base = declarative_base()


class FightersDB(Base):
    __tablename__ = "fighters"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    birth_date: Mapped[datetime] = mapped_column(nullable=False)
    wins: Mapped[int] = mapped_column(nullable=False, default=0)
    losses: Mapped[int] = mapped_column(nullable=False, default=0)
    draws: Mapped[Optional[int]] = mapped_column(default=0)
    no_contest: Mapped[Optional[int]] = mapped_column(default=0)
    height: Mapped[float] = mapped_column(nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False)
    reach: Mapped[Optional[float]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())  # created when the record its created
    updated_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # constraints
    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 5", name="name_min_length"),
        CheckConstraint("LENGTH(name) <=50", name="name_max_length"),
    )


class FightsDB(Base):
    __tablename__ = 'fights'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rounds: Mapped[RoundsEnum] = mapped_column(Enum(RoundsEnum), nullable=False)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    method: Mapped[WinningMethodEnum] = mapped_column(Enum(WinningMethodEnum), nullable=False)
    card: Mapped[int] = mapped_column(ForeignKey('cards.id'), nullable=False)
    red_corner: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    blue_corner: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    favorite: Mapped[Optional[int]] = mapped_column(ForeignKey('fighters.id'), nullable=True)
    winner: Mapped[Optional[int]] = mapped_column(ForeignKey('fighters.id'), nullable=True)
    round_finish: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    red_fighter = relationship('FightersDB', foreign_keys=[red_corner])
    blue_fighter = relationship('FightersDB', foreign_keys=[blue_corner])
    favorite_fighter = relationship('FightersDB', foreign_keys=[favorite])
    winner_fighter = relationship('FightersDB', foreign_keys=[winner])

    def __repr__(self):
        return f'<Fight(id={self.id}, red={self.red_corner}, blue={self.blue_corner})>'


class CardsDB(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    card_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    card_number: Mapped[int] = mapped_column(Integer, nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # constraints
    __table_args__ = (
        CheckConstraint("LENGTH(card_name) >= 5", name="card_name_min_length"),
        CheckConstraint("LENGTH(card_name) <=50", name="card_name_max_length"),
    )


class PicksDB(Base):
    __tablename__ = "picks"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fight_id: Mapped[int] = mapped_column(ForeignKey("fights.id"), nullable=False)
    winner_pick: Mapped[int] = mapped_column(ForeignKey("fighters.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    fight = relationship("FightsDB", foreign_keys=[fight_id])
    winner_picked = relationship("FightersDB", foreign_keys=[winner_pick])
