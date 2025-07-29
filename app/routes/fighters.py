from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import FightersDB
from app.db.session import get_db
from app.schemas.fighters import (
    DivisionEnum,
    Fighters,
    FightersCreate,
    FightersPatch,
    FightersUpdate,
)

router = APIRouter(prefix="/fighters", tags=["Fighters"])

# modular fuction paremeters
db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)


@router.get("/", response_model=list[Fighters], status_code=status.HTTP_200_OK)
def get_all_fighters(db: Session = db_dependency):
    fighters = db.query(FightersDB).all()
    if not fighters:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no fighters found")
    return fighters


@router.get("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def get_fighter(id: int, db: Session = db_dependency):
    fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {id} not found",
        )

    return fighter


@router.post("/", response_model=Fighters, status_code=status.HTTP_201_CREATED)
def create_fighter(
    name: str = required_form,
    division: str = required_form,
    birth_date: str = required_form,
    wins: int = required_form,
    losses: int = required_form,
    draws: int = required_form,
    no_contest: int = required_form,
    height: float = required_form,
    weight: float = required_form,
    reach: str | None = optional_form,
    db: Session = db_dependency,
):
    try:
        parsed_reach: float | None = float(reach) if reach not in (None, "") else None  # parse if its provided
        fighter_data = FightersCreate(
            name=name,
            division=DivisionEnum[division],
            birth_date=datetime.strptime(birth_date, "%Y-%m-%d").date(),
            wins=wins,
            losses=losses,
            draws=draws,
            no_contest=no_contest,
            height=height,
            weight=weight,
            reach=parsed_reach,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from None

    new_figher = FightersDB(
        name=fighter_data.name,
        division=fighter_data.division,
        birth_date=fighter_data.birth_date,
        wins=fighter_data.wins,
        losses=fighter_data.losses,
        draws=fighter_data.draws,
        no_contest=fighter_data.no_contest,
        height=fighter_data.height,
        weight=fighter_data.weight,
        reach=fighter_data.reach,
    )
    db.add(new_figher)
    db.commit()
    db.refresh(new_figher)
    return new_figher


@router.put("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def update_fighter(id: int, fighter: FightersUpdate, db: Session = db_dependency):
    db_fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not db_fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {id} not found",
        )

    for key, val in fighter.model_dump().items():
        setattr(db_fighter, key, val)

    db.commit()
    db.refresh(db_fighter)
    return db_fighter


@router.patch("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def update_fields_fighter(id: int, fighter: FightersPatch, db: Session = db_dependency):
    db_fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not db_fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {id} not found",
        )

    fighter_data = fighter.model_dump(exclude_unset=True, exclude_none=True)
    has_changes = False
    for key, val in fighter_data.items():
        if getattr(db_fighter, key) != val:
            setattr(db_fighter, key, val)
            has_changes = True

    if has_changes:
        db.commit()
        db.refresh(db_fighter)
    return db_fighter


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_fighter(id: int, db: Session = db_dependency):
    result = db.query(FightersDB).filter(FightersDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {id} not found",
        )

    db.commit()
    return None
