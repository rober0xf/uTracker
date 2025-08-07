from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fighters import FighterForm, Fighters, FightersUpdate

from .services import (
    create_fighter_service,
    create_fighter_with_features_service,
    get_all_fighters_service,
    get_fighter_service,
    remove_fighter_service,
    update_fighter_service,
)


def fighter_form(
    name: str = Form(...),
    division: str = Form(...),
    birth_date: str = Form(...),
    wins: int = Form(...),
    losses: int = Form(...),
    draws: str = Form(""),
    no_contest: str = Form(""),
    height: float = Form(...),
    weight: float = Form(...),
    reach: str = Form(""),
) -> FighterForm:
    return FighterForm(
        name=name,
        division=division,
        birth_date=birth_date,
        wins=wins,
        losses=losses,
        draws=None if draws == "" else int(draws),
        no_contest=None if no_contest == "" else int(no_contest),
        height=height,
        weight=weight,
        reach=None if reach == "" else float(reach),
    )


router = APIRouter(prefix="/fighters", tags=["Fighters"])

# modular fuction paremeters
db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)
fighter_form_dep = Depends(fighter_form)  # singleton


@router.get("/", response_model=list[Fighters], status_code=status.HTTP_200_OK)
def get_all_fighters(db: Session = db_dependency):
    return get_all_fighters_service(db)


@router.get("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def get_fighter(id: int, db: Session = db_dependency):
    return get_fighter_service(id, db)


@router.post("/", response_model=Fighters, status_code=status.HTTP_201_CREATED)
def create_fighter(db: Session = db_dependency, form_data: FighterForm = fighter_form_dep):
    data = create_fighter_service(form_data, db=db)
    return data


@router.put("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def update_fighter(id: int, fighter: FightersUpdate, db: Session = db_dependency):
    return update_fighter_service(id, fighter, db)


@router.patch("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def update_fields_fighter(id: int, fighter: FightersUpdate, db: Session = db_dependency):
    return update_fighter_service(id, fighter, db)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_fighter(id: int, db: Session = db_dependency):
    return remove_fighter_service(id, db)


@router.post("/features")
def create_features_fighter(fighter: FighterForm, db: Session = db_dependency):
    return create_fighter_with_features_service(fighter, db)
