from fastapi import APIRouter, status, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.cards import Cards, CardsCreate, CardsUpdate, CardsPatch
from app.db.session import get_db
from app.db.models import CardsDB

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.get("/{id}", response_model=Cards, status_code=status.HTTP_200_OK)
def get_card(id: int, db: Session = Depends(get_db)):
    card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    return card


@router.post("/", response_model=Cards, status_code=status.HTTP_201_CREATED)
def create_card(card_name: str = Form(...), card_date: str = Form(...), main_event_id: int = Form(...), db: Session = Depends(get_db)):
    try:
        card_data = CardsCreate(card_name=card_name, card_date=card_date, main_event_id=main_event_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    new_card = CardsDB(card_name=card_data.card_name, card_date=card_data.card_date, main_event_id=card_data.main_event_id)
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.put("/{id}", response_model=Cards, status_code=status.HTTP_200_OK)
def update_card(id: int, card: CardsUpdate, db: Session = Depends(get_db)):
    db_card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not db_card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")

    for key, val in card.model_dump().items():
        setattr(db_card, key, val)

    db.commit()
    db.refresh(db_card)
    return db_card


@router.patch("/{id}", response_model=Cards, status_code=status.HTTP_200_OK)
def update_fields_card(id: int, card: CardsPatch, db: Session = Depends(get_db)):
    db_card = db.query(CardsDB).filter(CardsDB.id == id).first()
    if not db_card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")

    card_data = card.model_dump(exclude_unset=True, exclude_none=True)
    has_changes = False
    for key, val in card_data.items():
        if getattr(db_card, key) != val:
            setattr(db_card, key, val)
            has_changes = True

    if has_changes:
        db.commit()
        db.refresh(db_card)
    return db_card


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_card(id: int, db: Session = Depends(get_db)):
    result = db.query(CardsDB).filter(CardsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card with id {id} not found")
    db.commit()
    return None
