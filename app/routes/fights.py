from fastapi import APIRouter, Depends, Form, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.db.models import FightersDB, FightsDB
from app.db.session import get_db
from app.schemas.fighters import DivisionEnum
from app.schemas.fights import Fights, FightsCreate, RoundsEnum, WinningMethodEnum
from app.core.templates import templates

router = APIRouter(prefix="/fights", tags=["Fights"])

db_dependency = Depends(get_db)
required_form = Form(...)
optional_form = Form(None)


@router.get(
    "/", name="list_fights", response_class=HTMLResponse, status_code=status.HTTP_200_OK
)
def get_all_fights(request: Request, db: Session = db_dependency):
    fights = db.query(FightsDB).all()
    if not fights:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no fights found"
        )
    return templates.TemplateResponse(
        "fights/list.html", {"request": request, "fights": fights}
    )


@router.get(
    "/{id}", name="get_fight", response_model=Fights, status_code=status.HTTP_200_OK
)
def get_fight(id: int, db: Session = db_dependency):
    fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not fight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fight with id {id} not found",
        )
    return fight


@router.post("/", response_model=Fights, status_code=status.HTTP_201_CREATED)
def create_fight(
    rounds: str = required_form,
    division: str = required_form,
    method: str | None = optional_form,
    card_id: int = required_form,
    red_corner: int = required_form,
    blue_corner: int = required_form,
    favorite: int | None = optional_form,
    winner: str | None = optional_form,
    round_finish: str | None = optional_form,
    db: Session = db_dependency,
):
    # first we check that the input ids exists
    red_fighter = db.query(FightersDB).filter(FightersDB.id == red_corner).first()
    if not red_fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {red_corner} not found",
        )
    blue_fighter = db.query(FightersDB).filter(FightersDB.id == blue_corner).first()
    if not blue_fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fighter with id {blue_corner} not found",
        )

    # validate the data
    try:
        parsed_method: WinningMethodEnum | None = (
            WinningMethodEnum[method] if method else None
        )
        parsed_winner: int | None = int(winner) if winner not in (None, "") else None
        parsed_round_finish: int | None = (
            int(round_finish) if round_finish not in (None, "") else None
        )
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
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid data"
        ) from None

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
    except Exception:
        db.rollback()  # remove changes so far
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to create fight",
        ) from None


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fight(id: int, db: Session = db_dependency):
    fight = db.query(FightsDB).filter(FightsDB.id == id).first()
    if not fight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"fight with id {id} not found",
        )

    try:
        db.delete(fight)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to delete fight}",
        ) from None
