from fastapi import (
    APIRouter,
    Depends,
    Form,
    status,
    HTTPException,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
from app.core.templates import templates

from app.db.session import get_db
from app.schemas.fighters import FighterForm, Fighters, FightersUpdate
from app.services.map_features import get_fighter_update_form

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


@router.get(
    "/",
    name="list_fighters",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def get_all_fighters(request: Request, db: Session = db_dependency):
    fighters = get_all_fighters_service(db)
    if not fighters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="no fighters found"
        )
    return templates.TemplateResponse(
        "fighters/list.html", {"request": request, "fighters": fighters}
    )


# create fighter form view
@router.get(
    "/create_fighter_view",
    name="create_fighter_form",
    response_class=HTMLResponse,
)
def create_fighter_form(request: Request):
    return templates.TemplateResponse("fighters/create.html", {"request": request})


# update fighter form view
@router.get(
    "{id}/update",
    name="update_fighter_form",
    response_class=HTMLResponse,
)
def update_fighter_form(request: Request, id: int, db: Session = db_dependency):
    fighter = get_fighter_service(id, db)
    if not fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found"
        )
    return templates.TemplateResponse(
        "fighters/update.html", {"request": request, "fighter": fighter}
    )


@router.get(
    "/{id}", name="get_fighter", response_model=Fighters, status_code=status.HTTP_200_OK
)
def get_fighter(request: Request, id: int, db: Session = db_dependency):
    fighter = get_fighter_service(id, db)
    if not fighter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="fighter not found"
        )
    return templates.TemplateResponse(
        "fighters/get.html", {"request": request, "fighter": fighter}
    )


@router.post(
    "/",
    name="create_fighter",
    response_class=HTMLResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fighter(
    request: Request,
    db: Session = db_dependency,
    form_data: FighterForm = fighter_form_dep,
):
    create_fighter_service(form_data, db=db)
    return RedirectResponse(
        url=request.url_for("list_fighters"), status_code=status.HTTP_303_SEE_OTHER
    )


# we need to use put as post because the template
@router.post(
    "/{id}/update",
    name="update_fighter",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
)
def update_fighter(
    request: Request,
    id: int,
    db: Session = db_dependency,
    form_data: FightersUpdate = Depends(get_fighter_update_form),
):
    update_fighter_service(id, form_data, db)
    return RedirectResponse(
        url=request.url_for("get_fighter", id=id), status_code=status.HTTP_303_SEE_OTHER
    )


@router.patch("/{id}", response_model=Fighters, status_code=status.HTTP_200_OK)
def update_fields_fighter(
    id: int, fighter: FightersUpdate, db: Session = db_dependency
):
    return update_fighter_service(id, fighter, db)


@router.delete("/{id}", name="delete_fighter", status_code=status.HTTP_200_OK)
def remove_fighter(request: Request, id: int, db: Session = db_dependency):
    remove_fighter_service(id, db)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_fighters"))
    return response


@router.post("/features")
async def create_features_fighter(fighter: FighterForm, db: Session = db_dependency):
    return await create_fighter_with_features_service(fighter, db)
