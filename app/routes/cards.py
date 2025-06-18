from fastapi import APIRouter, status, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.cards import Cards, CardsCreate
from app.db.session import get_db
from app.db.models import CardsDB
from typing import List, Optional

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("/", response_model=List[Cards], status_code=status.HTTP_200_OK)
def get_all_cards(db: Session = Depends(get_db)):
    cards = db.query(CardsDB).all()
    if not cards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no cards found")
    return cards


@router.get("/{id}", response_model=Cards, status_code=status.HTTP_200_OK)
def get_card(id: int, db: Session = Depends(get_db)):
    card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    return card


@router.post("/", response_model=Cards, status_code=status.HTTP_201_CREATED)
def create_card(
    card_name: str = Form(...),
    card_date: str = Form(...),
    card_number: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # handle manually if not card number provided
    if card_number == "":
        card_number = None
    else:
        try:
            card_number = int(card_number)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="card_number must be an uint if its provided")
    try:
        card_data = CardsCreate(card_name=card_name, card_date=card_date, card_number=card_number)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    new_card = CardsDB(
        card_name=card_data.card_name,
        card_date=card_data.card_date,
        card_number=card_data.card_number,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(id: int, db: Session = Depends(get_db)):
    result = db.query(CardsDB).filter(CardsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    db.commit()
    return None
