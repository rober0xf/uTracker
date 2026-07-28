from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.templates import templates
from app.infraestructure.database.repositories.cards_repository import CardRepository
from app.interfaces.api.injection import get_card_repository
from app.interfaces.schemas.card import CardCreate, CardRead
from app.services.cards import (
    create_card_service,
    delete_card_service,
    get_all_cards_service,
    get_card_by_id_service,
)

router = APIRouter(prefix="/cards", tags=["Cards"])


# modular function parameters
card_repo_dep = Depends(get_card_repository)


@router.get("/", name="list_cards", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_cards(request: Request, repo: CardRepository = card_repo_dep):
    try:
        cards = get_all_cards_service(repo)
        return templates.TemplateResponse("cards/list.html", {"request": request, "cards": cards})
    except ValueError:
        return templates.TemplateResponse("cards/not_found.html", {"request": request})


@router.get("/{id}/details", name="get_card", response_model=CardRead, status_code=status.HTTP_200_OK)
def get_card(request: Request, id: int, repo: CardRepository = card_repo_dep):
    card = get_card_by_id_service(id, repo)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="card not found")
    return templates.TemplateResponse("cards/get.html", {"request": request, "card": card})


# create card form view
@router.get("/create_card_view", name="create_card_form", response_class=HTMLResponse)
def create_card_form(request: Request):
    return templates.TemplateResponse("cards/create.html", {"request": request})


@router.post("/", name="create_card", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_card(request: Request, form_data: CardCreate = card_repo_dep, repo: CardRepository = card_repo_dep):
    card = create_card_service(form_data, repo)
    if not card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error creating card")
    return RedirectResponse(url=request.url_for("list_cards"), status_code=status.HTTP_303_SEE_OTHER)


# template form to update
@router.get("{id}/update", name="update_card_form", response_class=HTMLResponse)
def update_card_form(request: Request, id: int, repo: CardRepository = card_repo_dep):
    card = get_card_by_id_service(id, repo)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="card not found")
    return templates.TemplateResponse("cards/update.html", {"request": request, "card": card})


@router.delete("/{id}", name="delete_card", status_code=status.HTTP_200_OK)
def remove_card(request: Request, id: int, repo: CardRepository = card_repo_dep):
    delete_card_service(id, repo)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_cards"))
    return response
