from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Enum, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.schemas.fighters import DivisionEnum


Base = declarative_base()

class Fighters(Base):
    __tablename__ = "fighters"
    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(50), nullable=False, unique=True, index=True)
    division = Column(Enum(DivisionEnum), nullable=False)
    birth_date = Column(DateTime, nullable=False)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, default=0)
    no_contest = Column(Integer, default=0)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    reach = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now()) # created when the record its created
    updated_at = Column(DateTime, nullable=True)
