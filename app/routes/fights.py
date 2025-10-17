from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.fights import FightForm, Fights, FightsUpdate
from app.core.templates import templates
from app.services.fights import (
    create_fight_form_service,
    create_fight_service,
    get_all_fights_service,
    get_card_fighter_form,
    get_fight_by_id_service,
    get_fight_update_form,
    remove_fight_service,
    update_fight_service,
)

router = APIRouter(prefix="/fights", tags=["Fights"])

db_dependency = Depends(get_db)
fight_form_dep = Depends(create_fight_form_service)


@router.get("/", name="list_fights", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_fights(request: Request, db: Session = db_dependency):
    try:
        fights = get_all_fights_service(db)
        return templates.TemplateResponse("fights/list.html", {"request": request, "fights": fights})

    except ValueError:
        return templates.TemplateResponse("fights/not_found.html", {"request": request})
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no fights found")


@router.get("/{id}/details", name="get_fight", response_model=Fights, status_code=status.HTTP_200_OK)
def get_fight(request: Request, id: int, db: Session = db_dependency):
    fight = get_fight_by_id_service(id, db)
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return templates.TemplateResponse("fights/get.html", {"request": request, "fight": fight})


# template form to create
@router.get(
    "/create_fight_view",
    name="create_fight_form",
    response_class=HTMLResponse,
)
def create_fight_form(request: Request, db: Session = db_dependency):
    fighters, cards, message = get_card_fighter_form(db)
    return templates.TemplateResponse("fights/create.html", {"request": request, "fighters": fighters, "cards": cards, "message": message})


# update fight form view
@router.get(
    "{id}/update",
    name="update_fight_form",
    response_class=HTMLResponse,
)
def update_fight_form(request: Request, id: int, db: Session = db_dependency):
    fight = get_fight_by_id_service(id, db)
    fighters, cards, _ = get_card_fighter_form(db)

    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return templates.TemplateResponse("fights/update.html", {"request": request, "fight": fight, "fighters": fighters, "cards": cards})


@router.post(
    "/",
    name="create_fight",
    response_class=HTMLResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fight(
    request: Request,
    db: Session = db_dependency,
    form_data: FightForm = fight_form_dep,
):
    fight = create_fight_service(form_data, db)
    if not fight:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error creating fight")
    return RedirectResponse(url=request.url_for("list_fights"), status_code=status.HTTP_303_SEE_OTHER)


# we need to use put as post because the template
@router.post(
    "/{id}/update",
    name="update_fight",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def update_fight(
    request: Request,
    id: int,
    db: Session = db_dependency,
    form_data: FightsUpdate = Depends(get_fight_update_form),
):
    fight = update_fight_service(id, form_data, db)
    print(f"round: {form_data.round_finish}")
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return RedirectResponse(url=request.url_for("get_fight", id=id), status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/{id}", name="delete_fight", status_code=status.HTTP_200_OK)
def remove_fight(request: Request, id: int, db: Session = db_dependency):
    remove_fight_service(id, db)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_fights"))
    return response
