from datetime import date
from typing import Annotated

from fastapi import Form

from app.infraestructure.database.models.card_model import CardDB
from app.infraestructure.database.repositories.cards_repository import CardRepository
from app.interfaces.schemas.card import CardCreate


# get the data from the form
def create_card_form_service(
    card_name: Annotated[str, Form(...)],
    card_date: Annotated[date, Form(...)],
    card_number: Annotated[int | None, Form(None)],
) -> CardCreate:
    return CardCreate(card_name=card_name, card_date=card_date, card_number=card_number)


def create_card_service(card: CardCreate, repo: CardRepository):
    new_card = CardDB(**card.model_dump())
    return repo.create(new_card)


def get_all_cards_service(repo: CardRepository):
    cards = repo.get_all()
    if not cards:
        raise ValueError("no cards found")
    return cards


def get_card_by_id_service(id: int, repo: CardRepository):
    card = repo.get_by_id(id)
    if not card:
        raise ValueError(f"card with id {id} not found")
    return card


def delete_card_service(id: int, repo: CardRepository):
    result = repo.delete(id)
    if not result:
        raise ValueError("card not found")
    return None
