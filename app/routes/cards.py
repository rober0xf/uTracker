from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.templates import templates
from app.db.models import CardsDB, FightsDB
from app.db.session import get_db
from app.schemas.cards import CardForm, Cards
from app.services.cards import create_card_form_service, create_card_service, delete_card_service, get_all_cards_service, get_card_by_id_service

router = APIRouter(prefix="/cards", tags=["Cards"])

# modular function parameters
db_dependency = Depends(get_db)
card_form_dep = Depends(create_card_form_service)  # singleton


@router.get("/", name="list_cards", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_cards(request: Request, db: Session = db_dependency):
    try:
        cards = get_all_cards_service(db)
        return templates.TemplateResponse("cards/list.html", {"request": request, "cards": cards})

    except ValueError as e:
        return templates.TemplateResponse("cards/not_found.html", {"request": request})
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no cards found")


@router.get("/{id}/details", name="get_card", response_model=Cards, status_code=status.HTTP_200_OK)
def get_card(request: Request, id: int, db: Session = db_dependency):
    card = get_card_by_id_service(id, db)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"card not found")
    return templates.TemplateResponse("cards/get.html", {"request": request, "card": card})


# create card form view
@router.get("/create_card_view", name="create_card_form", response_class=HTMLResponse)
def create_card_form(request: Request):
    return templates.TemplateResponse("cards/create.html", {"request": request})


# template form to update
@router.get("{id}/update", name="update_card_form", response_class=HTMLResponse)
def update_card_form(request: Request, id: int, db: Session = db_dependency):
    card = get_card_by_id_service(id, db)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="card not found")
    return templates.TemplateResponse("cards/update.html", {"request": request, "card": card})


@router.post(
    "/",
    name="create_card",
    response_class=HTMLResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_card(request: Request, db: Session = db_dependency, form_data: CardForm = card_form_dep):
    card = create_card_service(form_data, db)
    if not card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error creating card")
    return RedirectResponse(url=request.url_for("list_cards"), status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/{id}", name="delete_card", status_code=status.HTTP_200_OK)
def remove_card(request: Request, id: int, db: Session = db_dependency):
    delete_card_service(id, db)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_cards"))
    return response
