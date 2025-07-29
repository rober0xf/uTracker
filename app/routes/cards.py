from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import CardsDB
from app.db.session import get_db
from app.schemas.cards import Cards, CardsCreate

router = APIRouter(prefix="/cards", tags=["Cards"])

# modular function parameters
db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)


@router.get("/", response_model=list[Cards], status_code=status.HTTP_200_OK)
def get_all_cards(db: Session = db_dependency):
    cards = db.query(CardsDB).all()
    if not cards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no cards found")
    return cards


@router.get("/{id}", response_model=Cards, status_code=status.HTTP_200_OK)
def get_card(id: int, db: Session = db_dependency):
    card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    return card


@router.post("/", response_model=Cards, status_code=status.HTTP_201_CREATED)
def create_card(
    card_name: str = required_form,
    card_date: str = required_form,
    card_number: str | None = optional_form,
    db: Session = db_dependency,
):
    card_number_int: int | None = None  # convert to int for processing

    # cast the date correctly
    try:
        card_date_datetime = datetime.strptime(card_date, "%Y-%m-%d")
    except ValueError:
        # from None hide the error. from err would show the error (better for debugging)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="card_date must be in %Y-%m-%d format") from None

    # handle card_number manually if not card number provided
    if card_number is not None and card_number != "":
        try:
            card_number_int = int(card_number)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="card_number must be an uint if its provided") from None

    try:
        card_data = CardsCreate(card_name=card_name, card_date=card_date_datetime, card_number=card_number_int)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from None

    if card_data.card_name and card_data.card_date:
        new_card = CardsDB(
            card_name=card_data.card_name,
            card_date=card_data.card_date,
            card_number=card_data.card_number,
        )
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return new_card
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="card_name and card_date are required")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(id: int, db: Session = db_dependency):
    result = db.query(CardsDB).filter(CardsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    db.commit()
    return None
