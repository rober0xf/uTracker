from datetime import datetime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import Enum, String
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey
from app.schemas.fighters import DivisionEnum
from app.schemas.fight import RoundsEnum, WinningMethodEnum
from typing import Optional


Base = declarative_base()


class Fighters(Base):
    __tablename__ = 'fighters'
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


class Fights(Base):
    __tablename__ = 'fights'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    rounds: Mapped[RoundsEnum] = mapped_column(Enum(RoundsEnum), nullable=False)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    method: Mapped[WinningMethodEnum] = mapped_column(Enum(WinningMethodEnum), nullable=False)
    card: Mapped[int] = mapped_column(ForeignKey('card.id'), nullable=False)
    red_corner: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    blue_corner: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    favorite: Mapped[Optional[int]] = mapped_column(ForeignKey('fighters.id'), nullable=True)
    winner: Mapped[Optional[int]] = mapped_column(ForeignKey('fighters.id'), nullable=True)
    round_finish: Mapped[Optional[int]] = mapped_column(nullable=True)
    time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    card = relationship('Card', back_populates='fights')
    red_fighter = relationship('Fighters', foreign_keys=[red_corner])
    blue_fighter = relationship('Fighters', foreign_keys=[blue_corner])
    favorite_fighter = relationship('Fighters', foreign_keys=[favorite])
    winner_fighter = relationship('Fighters', foreign_keys=[winner])

    def __repr__(self):
        return f'<Fight(id={self.id}, red={self.red_corner}, blue={self.blue_corner})>'


class Cards(Base):
    __tablename__ = 'cards'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    card_name: Mapped[str] = mapped_column(String(50), nullable=False)
    card_date: Mapped[datetime] = mapped_column(nullable=False)
    main_event_id: Mapped[int] = mapped_column(ForeignKey('fights.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationship definition
    main_event = relationship('Fights', foreign_keys=[main_event_id])
