from datetime import datetime

from fastapi import Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import FightersDB
from app.db.session import get_db
from app.schemas.fighters import DivisionEnum, FightersCreate, FightersPatch, FightersUpdate
from app.services.api_services import get_external_fighter_features
from app.services.map_features import update_fighter_features

db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)


def get_all_fighters_service(db: Session = db_dependency):
    fighters = db.query(FightersDB).all()
    if not fighters:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no fighters found")
    return fighters


def get_fighter_service(id: int, db: Session = db_dependency):
    fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not fighter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"fighter with id {id} not found")
    return fighter


def create_fighter_service(
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
        fighter_data = FightersCreate(
            name=name,
            division=DivisionEnum(division),
            birth_date=datetime.strptime(birth_date, "%Y-%m-%d").date(),
            wins=wins,
            losses=losses,
            draws=draws,
            no_contest=no_contest,
            height=height,
            weight=weight,
            reach=float(reach) if reach not in (None, "") else None,
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"invalid input: {str(e)}") from None

    new_figher = FightersDB(**fighter_data.model_dump())
    db.add(new_figher)
    db.commit()
    db.refresh(new_figher)
    return new_figher


def update_fighter_service(id: int, fighter: FightersUpdate, db: Session = db_dependency):
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


def update_fields_fighter_service(id: int, fighter: FightersPatch, db: Session = db_dependency):
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


def remove_fighter_service(id: int, db: Session = db_dependency):
    result = db.query(FightersDB).filter(FightersDB.id == id).delete(synchronize_session=False)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {id} not found",
        )

    db.commit()
    return None


def create_fighter_with_features_service(fighter_data, session: Session):
    if hasattr(fighter_data, "model_dump"):
        fighter_dict = fighter_data.model_dump()
    elif hasattr(fighter_data, "dict"):
        fighter_dict = fighter_data.dict()
    elif isinstance(fighter_data, dict):
        fighter_dict = fighter_data
    else:
        raise ValueError("fighter_data must be a dict or a pydantic model")

    fighter = FightersDB(**fighter_dict)
    session.add(fighter)
    session.flush()

    api_data = get_external_fighter_features(fighter.name)
    if api_data:
        update_fighter_features(session, fighter.id, api_data)
    session.commit()
    return fighter
