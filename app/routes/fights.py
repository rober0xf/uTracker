from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.db.models import FightsDB
from app.schemas.fights import Fights, FightsCreate, FightsPatch, FightsUpdate, RoundsEnum, WinningMethodEnum
from app.schemas.fighters import DivisionEnum
from app.db.session import get_db

router = APIRouter(prefix="/fights", tags=["fights"])


@router.get("/", response_model=Fights, status_code=status.HTTP_200_OK)
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
    method: str = Form(...),
    card: int = Form(...),
    red_corner: int = Form(...),
    blue_corner: int = Form(...),
    favorite: int | None = Form(None),
    winner: int | None = Form(None),
    round_finish: int | None = Form(None),
    time: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # validate the data
    try:
        fight_data = FightsCreate(
            rounds=RoundsEnum[rounds],
            division=DivisionEnum[division],
            method=WinningMethodEnum[method],
            card=card,
            red_corner=red_corner,
            blue_corner=blue_corner,
            favorite=favorite,
            winner=winner,
            round_finish=round_finish,
            time=time,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # create the instance fot the database
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
        time=fight_data.time,
    )
    db.add(new_fight)
    db.commit()
    db.refresh(new_fight)
    return new_fight


@router.put("/{id}", response_model=Fights, status_code=status.HTTP_200_OK)
def update_fight(id: int, fight: FightsUpdate, db: Session = Depends(get_db)):
    db_fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not db_fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fight with id {id} not found")

    # we get the key-val pairs
    for key, val in fight.model_dump().items():
        setattr(db_fight, key, val)

    db.commit()
    db.refresh(db_fight)
    return db_fight


@router.patch("/{id}", response_model=Fights, status_code=status.HTTP_200_OK)
def update_fields_fight(id: int, fight: FightsPatch, db: Session = Depends(get_db)):
    db_fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not db_fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fight with the id {id} not found")

    # only the provided fields. and exclude the none values from the response
    fight_data = fight.model_dump(exclude_unset=True, exclude_none=True)

    # update only the fields that have been changed
    has_changes = False
    for key, val in fight_data.items():
        if getattr(db_fight, key) != val:
            setattr(db_fight, key, val)
            has_changes = True

    if has_changes:
        db.commit()
        db.refresh(db_fight)

    return db_fight


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_fight(id: int, db: Session = Depends(get_db)):
    result = db.query(FightsDB).filter(FightsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fight with id {id} not found")

    db.commit()
    return None
