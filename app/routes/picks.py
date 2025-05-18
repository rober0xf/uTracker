from fastapi import APIRouter, status, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.schemas.picks import Picks, PicksCreate, PicksUpdate
from app.db.models import PicksDB
from app.db.session import get_db

router = APIRouter(prefix="/picks", tags=["Picks"])


@router.get("/{id}", response_model=Picks, status_code=status.HTTP_200_OK)
def get_pick(id: int, db: Session = Depends(get_db)):
    pick = db.query(PicksDB).filter(PicksDB.id == id).first()
    if not pick:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"pick with id {id} not found")
    return pick


@router.post("/", response_model=Picks, status_code=status.HTTP_201_CREATED)
def create_pick(fight_id: int = Form(...), winner_pick: int = Form(...), db: Session = Depends(get_db)):
    try:
        pick_data = PicksCreate(fight_id=fight_id, winner_pick=winner_pick)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    new_pick = PicksDB(fight_id=pick_data.fight_id, winner_pick=pick_data.winner_pick)
    db.add(new_pick)
    db.commit()
    db.refresh(new_pick)
    return new_pick


@router.put("/{id}", response_model=Picks, status_code=status.HTTP_200_OK)
def update_pick(id: int, pick=PicksUpdate, db: Session = Depends(get_db)):
    db_pick = db.query(PicksDB).filter(PicksDB.id == id).first()
    if not db_pick:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"pick with id {id} not found")

    for key, val in pick.model_dump().items():
        setattr(db_pick, key, val)

    db.commit()
    db.refresh(db_pick)
    return db_pick
