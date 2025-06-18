from app.schemas.fights import Fights, FightsCreate, RoundsEnum, WinningMethodEnum
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.db.models import FightsDB, FightersDB
from app.schemas.fighters import DivisionEnum
from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import List, Optional

router = APIRouter(prefix="/fights", tags=["Fights"])


@router.get("/", response_model=List[Fights], status_code=status.HTTP_200_OK)
def get_all_fights(db: Session = Depends(get_db)):
    fights = db.query(FightsDB).all()
    if not fights:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no fights found")
    return fights


@router.get("/{id}", response_model=Fights, status_code=status.HTTP_200_OK)
def get_fight(id: int, db: Session = Depends(get_db)):
    fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not fight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fight with id {id} not found",
        )
    return fight


@router.post("/", response_model=Fights, status_code=status.HTTP_201_CREATED)
def create_fight(
    rounds: str = Form(...),
    division: str = Form(...),
    method: str | None = Form(None),
    card_id: int = Form(...),
    red_corner: int = Form(...),
    blue_corner: int = Form(...),
    favorite: int | None = Form(None),
    winner: str | None = Form(None),
    round_finish: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # first we check that the input ids exists
    red_fighter = db.query(FightersDB).filter(FightersDB.id == red_corner).first()
    if not red_fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fighter with id {red_corner} not found")
    blue_fighter = db.query(FightersDB).filter(FightersDB.id == blue_corner).first()
    if not blue_fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fighter with id {blue_corner} not found")

    # validate the data
    try:
        parsed_method: Optional[WinningMethodEnum] = WinningMethodEnum[method] if method else None
        parsed_winner: Optional[int] = int(winner) if winner not in (None, "") else None
        parsed_round_finish: Optional[int] = int(round_finish) if round_finish not in (None, "") else None
        fight_data = FightsCreate(
            rounds=RoundsEnum[rounds],
            division=DivisionEnum[division],
            method=parsed_method,
            card=card_id,
            red_corner=red_corner,
            blue_corner=blue_corner,
            favorite=favorite,
            winner=parsed_winner,
            round_finish=parsed_round_finish,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid data: {str(e)}")

    # create the instance for the database
    new_fight = FightsDB(
        rounds=fight_data.rounds,
        division=fight_data.division,
        method=fight_data.method,
        card=fight_data.card,
        red_corner=fight_data.red_corner,
        blue_corner=fight_data.blue_corner,
        favorite=fight_data.favorite,
        winner=fight_data.winner,
        round_finish=fight_data.round_finish,
    )

    try:
        db.add(new_fight)
        db.commit()
        db.refresh(new_fight)
        return new_fight
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create fight: {str(e)}")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fight(id: int, db: Session = Depends(get_db)):
    fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fight with id {id} not found")

    try:
        db.delete(fight)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete fight: {str(e)}")
