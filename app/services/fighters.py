from domain.enums.enums import DivisionEnum
from fastapi import Form
from infraestructure.database.models.fighter_model import FighterDB
from infraestructure.database.repositories.fighters_repository import FighterRepository
from interfaces.schemas.fighters import FighterBase, FighterForm, FighterUpdate
from services.api_services import get_external_fighter_features


def get_all_fighters_service(repo: FighterRepository):
    fighters = repo.get_all()
    if not fighters:
        raise ValueError("no fighters found")
    return fighters


def get_fighter_by_id_service(id: int, repo: FighterRepository):
    fighter = repo.get_by_id(id)
    if not fighter:
        raise ValueError("fighter with id not found")
    return fighter


def create_fighter_service(fighter_form: FighterForm, repo: FighterRepository):
    # handle the data conversion and validation with the class method
    fighter_data = fighter_form.to_fighter_base_data()
    if not fighter_data:
        raise ValueError("error parsing the fighter data")

    validated_fighter = FighterBase(**fighter_data)
    fighter_db = FighterDB(**validated_fighter.model_dump())
    return repo.create(fighter_db)


# works for put and patch
def update_fighter_service(id: int, fighter: FighterUpdate, repo: FighterRepository):
    db_fighter = repo.get_by_id(id)
    if not db_fighter:
        raise ValueError("fighter not found")

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
    FighterBase(**current_data)  # raise error if data is invalid

    return repo.update(db_fighter, update_data)


def delete_fighter_service(id: int, repo: FighterRepository):
    result = repo.delete(id)
    if not result:
        raise ValueError("fighter not found")
    return None


# external api
async def create_fighter_with_features_service(fighter_form: FighterForm, repo: FighterRepository):
    fighter_data = fighter_form.to_fighter_base_data()
    validated_fighter = FighterBase(**fighter_data)
    fighter_db = FighterDB(**validated_fighter.model_dump())
    fighter = repo.create(fighter_db)

    try:
        api_data = await get_external_fighter_features(fighter.name)

        if api_data:
            repo.update_features(fighter.id, api_data)

    except Exception as e:
        print(f"could not update features: {str(e)}")

    return fighter


# we need to use this service because the way fastapi handles forms
async def get_fighter_update_form(
    name: str = Form(None),
    division: str = Form(None),
    wins: str = Form(None),
    losses: str = Form(None),
    draws: str = Form(None),
    no_contest: str = Form(None),
    height: str = Form(None),
    weight: str = Form(None),
    reach: str = Form(None),
) -> FighterUpdate:
    parsed_division = DivisionEnum(division) if division else None

    return FighterUpdate(
        name=name if name else None,
        division=parsed_division,
        birth_date=None,
        wins=int(wins) if wins and wins.strip() else None,
        losses=int(losses) if losses and losses.strip() else None,
        draws=int(draws) if draws and draws.strip() else None,
        no_contest=int(no_contest) if no_contest and no_contest.strip() else None,
        height=float(height) if height and height.strip() else None,
        weight=float(weight) if weight and weight.strip() else None,
        reach=float(reach) if reach and reach.strip() else None,
    )
