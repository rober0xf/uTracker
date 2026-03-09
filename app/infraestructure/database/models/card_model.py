from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base_model import Base


class CardDB(Base):
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
