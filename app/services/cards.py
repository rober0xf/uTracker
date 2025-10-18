from fastapi import Depends, Form
from sqlalchemy.orm import Session

from app.db.models import CardsDB
from app.db.session import get_db
from app.schemas.cards import CardForm, CardsBase


db_dependency = Depends(get_db)


# get the data from the form
def create_card_form_service(
    card_name: str = Form(...),
    card_date: str = Form(...),
    card_number: str | None = Form(None),
) -> CardForm:
    return CardForm(
        card_name=card_name,
        card_date=card_date,
        card_number=int(card_number) if card_number else None,
    )


def get_all_cards_service(db: Session = db_dependency):
    cards = db.query(CardsDB).all()
    if not cards:
        raise ValueError("no cards found")
    return cards


def get_card_by_id_service(id: int, db: Session = db_dependency):
    card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not card:
        raise ValueError("card with id {id} not found")
    return card


def create_card_service(card_form: CardForm, db: Session = db_dependency):
    card_data = card_form.to_cards_base_data()
    if not card_data:
        raise ValueError("error parsing the card data")

    validated_card = CardsBase(**card_data)
    new_card = CardsDB(**validated_card.model_dump())
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


def delete_card_service(id: int, db: Session = db_dependency):
    result = db.query(CardsDB).filter(CardsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise ValueError("card not found")
    db.commit()
    return None
