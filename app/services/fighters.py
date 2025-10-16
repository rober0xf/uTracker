from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.models import FightersDB
from app.db.session import get_db
from app.schemas.fighters import FighterForm, FightersBase, FightersUpdate
from app.services.api_services import get_external_fighter_features
from app.services.map_features import update_fighter_features


db_dependency = Depends(get_db)


def get_all_fighters_service(db: Session = db_dependency):
    fighters = db.query(FightersDB).all()
    if not fighters:
        raise ValueError("no fighters found")
    return fighters


def get_fighter_service(id: int, db: Session = db_dependency):
    fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not fighter:
        raise ValueError("fighter with id {id} not found")
    return fighter


def create_fighter_service(fighter_form: FighterForm, db: Session = db_dependency):
    fighter_data = fighter_form.to_fighters_base_data()  # handle the data conversion and validation with the class method
    if not fighter_data:
        raise ValueError("error parsing the fighter data")
    validated_fighter = FightersBase(**fighter_data)  # validate the model

    new_fighter = FightersDB(**validated_fighter.model_dump())
    db.add(new_fighter)
    db.commit()
    db.refresh(new_fighter)
    return new_fighter


# works for put and patch
def update_fighter_service(id: int, fighter: FightersUpdate, db: Session = db_dependency):
    db_fighter = db.query(FightersDB).filter(FightersDB.id == id).first()
    if not db_fighter:
        raise ValueError("fighter with id {id} not found")

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


def remove_fighter_service(id: int, db: Session = db_dependency):
    result = db.query(FightersDB).filter(FightersDB.id == id).delete(synchronize_session=False)
    if not result:
        raise ValueError("fighter with id {id} not found")

    db.commit()
    return None


async def create_fighter_with_features_service(fighter_form: FighterForm, session: Session):
    try:
        fighter_data = fighter_form.to_fighters_base_data()
        validated_fighter = FightersBase(**fighter_data)

        fighter = FightersDB(**validated_fighter.model_dump())
        session.add(fighter)
        session.flush()

        api_data = None
        try:
            api_data = await get_external_fighter_features(fighter.name)
        except Exception as e:
            print(f"could not fetch external data for {fighter.name}:{str(e)}")

        if api_data:
            try:
                update_fighter_features(session, fighter.id, api_data)
            except Exception as e:
                print(f"could not update features: {str(e)}")

        session.commit()
        session.refresh(fighter)
        return fighter

    except Exception as e:
        session.rollback()
        raise ValueError("error with the database: {str(e)}") from None
