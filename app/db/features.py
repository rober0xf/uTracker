from datetime import datetime
from typing import final

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# extra fields for the model predictor
@final  # to not override, needed for fighter relationship
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

    fighter = relationship("FightersDB", back_populates="features")
