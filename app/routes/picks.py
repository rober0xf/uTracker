from fastapi import APIRouter, status, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from app.schemas.picks import Picks, PicksCreate
from app.db.models import PicksDB, FightsDB, FightersDB
from app.db.session import get_db

router = APIRouter(prefix="/picks", tags=["Picks"])


@router.get("/", response_model=List[Picks], status_code=status.HTTP_200_OK)
def get_all_picks(db: Session = Depends(get_db)):
    picks = db.query(PicksDB).all()
    if not picks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no picks found")
    return picks


@router.get("/{id}", response_model=Picks, status_code=status.HTTP_200_OK)
def get_pick(id: int, db: Session = Depends(get_db)):
    pick = db.query(PicksDB).filter(PicksDB.id == id).first()
    if not pick:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"pick with id {id} not found")
    return pick


@router.post("/", response_model=Picks, status_code=status.HTTP_201_CREATED)
def create_pick(fight_id: int = Form(...), winner_pick: int = Form(...), db: Session = Depends(get_db)):
    # first we check that the input ids exists
    fight = db.query(FightsDB).filter(FightsDB.id == fight_id).first()
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fight with id {fight_id} not found")
    fighter = db.query(FightersDB).filter(FightersDB.id == winner_pick).first()
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fighter with id {winner_pick} not found")

    # now we parse the info
    try:
        pick_data = PicksCreate(fight_id=fight_id, winner_pick=winner_pick)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    new_pick = PicksDB(fight_id=pick_data.fight_id, winner_pick=pick_data.winner_pick)
    db.add(new_pick)
    db.commit()
    db.refresh(new_pick)
    return new_pick
