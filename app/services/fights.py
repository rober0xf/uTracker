from fastapi import Depends, Form
from sqlalchemy.orm import Session

from app.db.models import CardsDB, FightersDB, FightsDB
from app.db.session import get_db
from app.schemas.fighters import DivisionEnum
from app.schemas.fights import FightForm, FightsBase, FightsUpdate, RoundsEnum, WinningMethodEnum


db_dependency = Depends(get_db)


# get the data from the form
def create_fight_form_service(
    rounds: str = Form(...),
    division: str = Form(..., alias="division"),
    card_id: int = Form(...),
    red_corner: int = Form(..., alias="red_corner"),
    blue_corner: int = Form(..., alias="blue_corner"),
    method: str | None = Form(None),
    favorite: str | None = Form(None),
    winner: str | None = Form(None),
    round_finish: str | None = Form(None),
    fight_date: str = Form(...),
) -> FightForm:
    return FightForm(
        rounds=rounds,
        division=division,
        card_id=card_id,
        red_corner=red_corner,
        blue_corner=blue_corner,
        method=method if method else None,
        favorite=int(favorite) if favorite else None,
        winner=int(winner) if winner else None,
        round_finish=int(round_finish) if round_finish else None,
        fight_date=fight_date,
    )


def get_card_fighter_form(db: Session = db_dependency):
    fighters = db.query(FightersDB).all()  # we need to set the fighters for the form
    cards = db.query(CardsDB).all()  # also here
    message = None

    if not fighters:
        message = "no fighters found, create fighters"

    elif not cards:
        message = "no cards found, create fighters"

    return fighters, cards, message


def get_all_fights_service(db: Session = db_dependency):
    fights = db.query(FightsDB).all()
    if not fights:
        raise ValueError("no fights found")

    return fights


def get_fight_by_id_service(id: int, db: Session = db_dependency):
    fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not fight:
        raise ValueError("fight doesnt exists")
    return fight


def create_fight_service(fight_form: FightForm, db: Session) -> FightsDB:
    fight_data = fight_form.to_fights_base_data()
    if not fight_data:
        raise ValueError("error parsing fight data")

    # check if the fighter exists
    red_fighter = db.query(FightersDB).filter(FightersDB.id == fight_form.red_corner).first()
    if not red_fighter:
        raise ValueError(
            f"fighter with id {fight_form.red_corner} not found",
        )

    blue_fighter = db.query(FightersDB).filter(FightersDB.id == fight_form.blue_corner).first()
    if not blue_fighter:
        raise ValueError(
            f"fighter with id {fight_form.blue_corner} not found",
        )

    # create and validate
    validated_fight = FightsBase(**fight_data)
    new_fight = FightsDB(**validated_fight.model_dump())
    db.add(new_fight)
    db.commit()
    db.refresh(new_fight)
    return new_fight


# works for put and patch
def update_fight_service(id: int, fight: FightsUpdate, db: Session = db_dependency):
    db_fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not db_fight:
        raise ValueError("fight not found")

    # get the updated data
    update_data = fight.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        return db_fight

    # validata the data
    current_data = {
        "rounds": db_fight.rounds,
        "division": db_fight.division,
        "method": db_fight.method,
        "card": db_fight.card,
        "red_corner": db_fight.red_corner,
        "blue_corner": db_fight.blue_corner,
        "favorite": db_fight.favorite,
        "winner": db_fight.winner,
        "fight_date": db_fight.fight_date,
        "round_finish": db_fight.round_finish,
    }
    current_data.update(update_data)  # apply the updates
    FightsBase(**current_data)  # raise error if data is invalid

    changes_made = []
    for field_name, new_value in update_data.items():
        old_value = getattr(db_fight, field_name)
        if old_value != new_value:
            setattr(db_fight, field_name, new_value)
            changes_made.append(new_value)

    if changes_made:
        db.commit()
        db.refresh(db_fight)
    return db_fight


def remove_fight_service(id: int, db: Session = db_dependency):
    result = db.query(FightsDB).filter(FightsDB.id == id).delete(synchronize_session=False)
    if not result:
        raise ValueError("fight not found")
    db.commit()
    return None


async def get_fight_update_form(
    fight_date: str = Form(None),
    rounds: str = Form(None),
    division: str = Form(None),
    method: str | None = Form(None, alias="method"),
    card: str = Form(None),
    red_corner: str = Form(None),
    blue_corner: str = Form(None),
    favorite: str = Form(None),
    winner: str = Form(None),
    round_finish: str | None = Form(None, alias="round_finish"),
) -> FightsUpdate:
    return FightsUpdate(
        rounds=RoundsEnum(int(rounds)) if rounds else None,
        division=DivisionEnum(division) if division else None,
        method=WinningMethodEnum(method) if method else None,
        card=int(card) if card and card.strip() else None,
        red_corner=int(red_corner) if red_corner and red_corner.strip() else None,
        blue_corner=int(blue_corner) if blue_corner and blue_corner.strip() else None,
        favorite=int(favorite) if favorite and favorite.strip() else None,
        winner=int(winner) if winner and winner.strip() else None,
        round_finish=int(round_finish) if round_finish and round_finish.strip() else None,
        fight_date=fight_date if fight_date else None,
    )
