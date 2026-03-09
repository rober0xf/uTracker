from typing import cast

from core.templates import templates
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from infraestructure.database.repositories.cards_repository import CardRepository
from infraestructure.database.repositories.fighters_repository import FighterRepository
from infraestructure.database.repositories.fights_repository import FightRepository
from schemas.fights import FightForm, FightRead, FightUpdate
from services.fights import (
    create_fight_service,
    delete_fight_service,
    get_all_fights_service,
    get_card_fighter_form,
    get_fight_by_id_service,
    get_fight_form,
    get_fight_update_form,
    predict_fight_service,
    update_fight_service,
)
from services.predictor import (
    FightPredictionRequest,
    FightPredictionResponse,
)

from .injection import get_card_repository, get_fight_repository, get_fighter_repository

router = APIRouter(prefix="/fights", tags=["Fights"])

fight_repo_dep = Depends(get_fight_repository)
fighter_repo_dep = Depends(get_fighter_repository)
card_repo_dep = Depends(get_card_repository)

fight_update_form_dep = Depends(get_fight_update_form)
fight_form_dep = Depends(get_fight_form)


@router.get("/", name="list_fights", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def get_all_fights(request: Request, repo: FightRepository = fight_repo_dep):
    try:
        fights = get_all_fights_service(repo)
        return templates.TemplateResponse("fights/list.html", {"request": request, "fights": fights})

    except ValueError:
        return templates.TemplateResponse("fights/not_found.html", {"request": request})


@router.get("/{id}/details", name="get_fight", response_model=FightRead, status_code=status.HTTP_200_OK)
def get_fight(request: Request, id: int, repo: FightRepository = fight_repo_dep):
    fight = get_fight_by_id_service(id, repo)
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return templates.TemplateResponse("fights/get.html", {"request": request, "fight": fight})


# template form to create
@router.get("/create_fight_view", name="create_fight_form", response_class=HTMLResponse)
def create_fight_form(request: Request, fighter_repo: FightRepository = fight_repo_dep, card_repo: CardRepository = card_repo_dep):
    fighters, cards, message = get_card_fighter_form(fighter_repo, card_repo)
    return templates.TemplateResponse(
        "fights/create.html",
        {"request": request, "fighters": fighters, "cards": cards, "message": message},
    )


# update fight form view
@router.get("/{id}/update", name="update_fight_form", response_class=HTMLResponse)
def update_fight_form(request: Request, id: int, fight_repo: FightRepository = fight_repo_dep, card_repo: CardRepository = card_repo_dep):
    fight = get_fight_by_id_service(id, fight_repo)
    fighters, cards, _ = get_card_fighter_form(fight_repo, card_repo)

    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return templates.TemplateResponse(
        "fights/update.html",
        {"request": request, "fight": fight, "fighters": fighters, "cards": cards},
    )


@router.post("/", name="create_fight", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def create_fight(
    request: Request, form_data: FightForm = fight_form_dep, fight_repo: FightRepository = fight_repo_dep, fighter_repo: FighterRepository = fighter_repo_dep
):
    fight = create_fight_service(form_data, fight_repo, fighter_repo)
    if not fight:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="error creating fight")
    return RedirectResponse(url=request.url_for("list_fights"), status_code=status.HTTP_303_SEE_OTHER)


# we need to use put as post because the template
@router.post("/{id}/update", name="update_fight", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def update_fight(request: Request, id: int, form_data: FightUpdate = fight_update_form_dep, repo: FightRepository = fighter_repo_dep):
    fight = update_fight_service(id, form_data, repo)
    if not fight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="fight not found")
    return RedirectResponse(url=request.url_for("get_fight", id=id), status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/{id}", name="delete_fight", status_code=status.HTTP_200_OK)
def remove_fight(request: Request, id: int, repo: FightRepository = fight_repo_dep):
    delete_fight_service(id, repo)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = str(request.url_for("list_fights"))
    return response


# pytorch model
@router.post("/predict", response_model=FightPredictionResponse)
async def predict_fight(payload: FightPredictionRequest, repo: FighterRepository = fight_repo_dep):
    return predict_fight_service(payload, repo)


@router.post("/predict_html", response_class=HTMLResponse)
async def predict_fight_html(request: Request, repo: FighterRepository = fight_repo_dep):
    try:
        form = await request.form()
        red_id = int(cast(str, form["red_corner_id"]))
        blue_id = int(cast(str, form["blue_corner_id"]))

        payload = FightPredictionRequest(
            red_corner_id=red_id,
            blue_corner_id=blue_id,
        )
        print(f"prediction: {payload.red_corner_id}, {payload.blue_corner_id}")

        result = await predict_fight(payload, repo)
        print(f"real prediction: {result.red_corner_win_probability}, {result.blue_corner_win_probability}")
        html = f"""
        <div>
          <strong style='color: red;'>Red win:</strong> {result.red_corner_win_probability:.2%}<br>
          <strong style='color: blue;'>Blue win:</strong> {result.blue_corner_win_probability:.2%}
        </div>
        """
        return HTMLResponse(html)
    except Exception as e:
        print(f"error: {str(e)}")
        import traceback

        traceback.print_exc()
        return HTMLResponse(
            f"<div style='color: red;'>error: {str(e)}</div>",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# # testing
# @router.post("/insert-features")
# async def insert_features(fighter_id: int, repo: FighterRepository = fight_repo_dep):
#     features = FighterFeatures(
#         fighter_id=fighter_id,
#         avg_sig_str_landed=2.53,
#         avg_sig_str_pct=0.69,
#         avg_sub_att=0.00,
#         avg_td_landed=4.04,
#         avg_td_pct=0.59,
#         wins_by_ko=1,
#         wins_by_submission=6,
#     )
#     db.add(features)
#     db.commit()
#     return {"status": "good"}
