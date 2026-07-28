from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infraestructure.database.repositories.cards_repository import CardRepository
from app.infraestructure.database.repositories.fighters_repository import FighterRepository
from app.infraestructure.database.repositories.fights_repository import FightRepository
from app.infraestructure.database.session import get_db

DBSession = Annotated[Session, Depends(get_db)]


def get_card_repository(db: DBSession) -> CardRepository:
    return CardRepository(db)


def get_fight_repository(db: DBSession) -> FightRepository:
    return FightRepository(db)


def get_fighter_repository(db: DBSession) -> FighterRepository:
    return FighterRepository(db)
