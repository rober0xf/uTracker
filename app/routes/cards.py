from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import CardsDB, FightsDB
from app.db.session import get_db
from app.schemas.cards import Cards, CardsCreate, CardsResponse

router = APIRouter(prefix="/cards", tags=["Cards"])

# modular function parameters
db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)


@router.get("/", response_model=list[CardsResponse], status_code=status.HTTP_200_OK)
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


@router.post("/", response_model=CardsResponse, status_code=status.HTTP_201_CREATED)
def create_card(card_name: str = required_form, card_date: str = required_form, card_number: str | None = optional_form, db: Session = db_dependency):
    card_data = CardsCreate(card_name=card_name, card_date=card_date, card_number=card_number)  # validate with pydantic
    new_card = CardsDB(**card_data.model_dump())
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(id: int, db: Session = db_dependency):
    db.query(FightsDB).filter(FightsDB.card == id).delete(synchronize_session=False)
    result = db.query(CardsDB).filter(CardsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    db.commit()
    return None
