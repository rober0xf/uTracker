from datetime import datetime

from fastapi import Depends, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import FightersDB
from app.db.session import get_db
from app.schemas.fighters import FighterForm, FightersBase, FightersUpdate
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


def create_fighter_service(fighter_form: FighterForm, db: Session = db_dependency):
    try:
        fighter_data = fighter_form.to_fighters_base_data()  # handle the data conversion and validation with the class method
        validated_fighter = FightersBase(**fighter_data)  # validate the model

        new_fighter = FightersDB(**validated_fighter.model_dump())
        db.add(new_fighter)
        db.commit()
        db.refresh(new_fighter)
        return new_fighter

    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"invalid input: {str(e)}") from None


def update_fighter_service(id: int, fighter: FightersUpdate, db: Session = db_dependency):
    try:
        db_fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
        if not db_fighter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"fighter with id {id} not found",
            )

        # get the updated data
        update_data = fighter.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return db_fighter

        # validata the data
        current_data = {
            "name": db_fighter.name,
            "division": db_fighter.division,
            "birth_date": db_fighter.birth_date,
            "wins": db_fighter.wins,
            "losses": db_fighter.losses,
            "draws": db_fighter.draws,
            "no_contest": db_fighter.no_contest,
            "height": db_fighter.height,
            "weight": db_fighter.weight,
            "reach": db_fighter.reach,
        }
        current_data.update(update_data)  # apply the updates

        FightersBase(**current_data)  # raise error if data is invalid

        changes_made = []
        for field_name, new_value in update_data.items():
            old_value = getattr(db_fighter, field_name)
            if old_value != new_value:
                setattr(db_fighter, field_name, new_value)
                changes_made.append(new_value)

        if changes_made:
            db_fighter.updated_at = datetime.now()
            db.commit()
            db.refresh(db_fighter)
        return db_fighter

    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="error updating the fighter") from None


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
