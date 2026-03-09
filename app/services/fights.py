import torch
from domain.enums.enums import DivisionEnum, RoundsEnum, WinningMethodEnum
from fastapi import Depends, Form
from infraestructure.database.models.fight_model import FightDB
from infraestructure.database.repositories.cards_repository import CardRepository
from infraestructure.database.repositories.fighters_repository import FighterRepository
from infraestructure.database.repositories.fights_repository import FightRepository
from interfaces.schemas.fights import FightBase, FightForm, FightUpdate, FightUpdateForm
from services.predictor import (
    FightPredictionRequest,
    FightPredictionResponse,
    get_or_fetch_fighter_features,
    get_pytorch_model,
    prepare_model_input,
)


# get the data from the form
def get_fight_form(
    rounds: str = Form(...),
    division: str = Form(...),
    method: str | None = Form(None),
    card: str = Form(...),
    red_corner: int = Form(...),
    blue_corner: int = Form(...),
    favorite: str = Form(...),
    winner: str = Form(...),
    round_finish: str | None = Form(None),
    fight_date: str = Form(...),
) -> FightForm:
    return FightForm(
        rounds=rounds,
        division=division,
        method=method,
        card=card,
        red_corner=red_corner,
        blue_corner=blue_corner,
        favorite=favorite,
        winner=winner,
        round_finish=round_finish,
        fight_date=fight_date,
    )


# for html render
def get_card_fighter_form(fighter_repo: FightRepository, card_repo: CardRepository):
    fighters = fighter_repo.get_all()  # we need to set the fighters for the form
    cards = card_repo.get_all()  # also here
    message = None

    if not fighters:
        message = "no fighters found, create fighters"

    elif not cards:
        message = "no cards found, create fighters"

    return fighters, cards, message


def get_all_fights_service(repo: FightRepository):
    fights = repo.get_all()
    if not fights:
        raise ValueError("no fights found")
    return fights


def get_fight_by_id_service(id: int, repo: FightRepository):
    fight = repo.get_by_id(id)
    if not fight:
        raise ValueError(f"fight with id {id} not found")
    return fight


def create_fight_service(fight_form: FightForm, fight_repo: FightRepository, fighter_repo: FighterRepository):
    fight_data = fight_form.to_fights_base_data()
    red_fighter = fighter_repo.get_by_id(fight_form.red_corner)
    if not red_fighter:
        raise ValueError("red corner not found")

    blue_fighter = fighter_repo.get_by_id(fight_form.blue_corner)
    if not blue_fighter:
        raise ValueError("blue corner not found")

    validated_fighter = FightBase(**fight_data)
    fight_db = FightDB(**validated_fighter.model_dump())
    return fight_repo.create(fight_db)


# works for put and patch
def update_fight_service(id: int, fight: FightUpdate, repo: FightRepository):
    db_fight = repo.get_by_id(id)
    if not db_fight:
        raise ValueError("fight not found")

    update_data = fight.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        return db_fight

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
    FightBase(**current_data)  # raise error if data is invalid

    changes_made = False
    for field_name, new_value in update_data.items():
        if getattr(db_fight, field_name) != new_value:
            setattr(db_fight, field_name, new_value)
            changes_made = True

    if changes_made:
        repo.save(db_fight)

    return db_fight


def delete_fight_service(id: int, repo: FightRepository):
    result = repo.delete(id)
    if not result:
        raise ValueError("fight not found")
    return None


async def get_fight_update_form(form: FightUpdateForm = Depends()) -> FightUpdate:
    return FightUpdate(
        rounds=RoundsEnum(form.rounds) if form.rounds else None,
        division=DivisionEnum(form.division) if form.division else None,
        method=WinningMethodEnum(form.method) if form.method else None,
        **form.model_dump(exclude={"rounds", "division", "method"}),
    )


def predict_fight_service(payload: FightPredictionRequest, repo: FighterRepository) -> FightPredictionResponse:
    model = get_pytorch_model()
    red_features = get_or_fetch_fighter_features(payload.red_corner_id, repo)
    blue_features = get_or_fetch_fighter_features(payload.blue_corner_id, repo)
    model_input = prepare_model_input(red_features, blue_features)

    with torch.no_grad():
        output = model(model_input)
        probability = torch.sigmoid(output)[0][0]

    red_prob = float(probability.cpu())
    blue_prob = 1.0 - red_prob  # the probs are sigmoid, not softmax

    return FightPredictionResponse(
        red_corner_id=payload.red_corner_id,
        blue_corner_id=payload.blue_corner_id,
        red_corner_win_probability=red_prob,
        blue_corner_win_probability=blue_prob,
    )
