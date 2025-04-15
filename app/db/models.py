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

