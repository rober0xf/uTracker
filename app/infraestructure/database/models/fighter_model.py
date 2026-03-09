from datetime import date, datetime

from domain.enums.enums import DivisionEnum
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

from .base_model import Base


class FighterDB(Base):
    __tablename__: str = "fighters"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    division: Mapped[DivisionEnum] = mapped_column(Enum(DivisionEnum), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    draws: Mapped[int | None] = mapped_column(Integer, nullable=True)
    no_contest: Mapped[int | None] = mapped_column(Integer, nullable=True)
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


class FighterFeatures(Base):
    __tablename__: str = "fighter_features"

    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"), primary_key=True)
    avg_sig_str_landed: Mapped[float] = mapped_column(Float, default=0.0)
    avg_sig_str_pct: Mapped[float] = mapped_column(Float, default=0.0)
    avg_sub_att: Mapped[float] = mapped_column(Float, default=0.0)
    avg_td_landed: Mapped[float] = mapped_column(Float, default=0.0)
    avg_td_pct: Mapped[float] = mapped_column(Float, default=0.0)
    wins_by_ko: Mapped[int] = mapped_column(Integer, default=0)
    wins_by_submission: Mapped[int] = mapped_column(Integer, default=0)

    updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=func.now(), server_default=func.now())

    fighter: Mapped["FighterDB"] = relationship("FightersDB", back_populates="features")
