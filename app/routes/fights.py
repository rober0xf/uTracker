from typing import cast
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session
import torch

from app.db.models import FighterFeatures
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
from app.services.predictor import FightPredictionRequest, FightPredictionResponse, get_or_fetch_fighter_features, get_pytorch_model, prepare_model_input

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


# pytorch model
@router.post("/predict", response_model=FightPredictionResponse)
async def predict_fight(payload: FightPredictionRequest, db: Session = db_dependency):
    model = get_pytorch_model()
    red_features = await get_or_fetch_fighter_features(payload.red_corner_id, db)
    blue_features = await get_or_fetch_fighter_features(payload.blue_corner_id, db)
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


@router.post("/predict_html", response_class=HTMLResponse)
async def predict_fight_html(request: Request, db: Session = db_dependency):
    try:
        form = await request.form()
        red_id = int(cast(str, form["red_corner_id"]))
        blue_id = int(cast(str, form["blue_corner_id"]))

        payload = FightPredictionRequest(
            red_corner_id=red_id,
            blue_corner_id=blue_id,
        )
        print(f"prediction: {payload.red_corner_id}, {payload.blue_corner_id}")

        result = await predict_fight(payload, db)
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
        return HTMLResponse(f"<div style='color: red;'>error: {str(e)}</div>", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# testing
@router.post("/insert-features")
async def insert_features(fighter_id: int, db: Session = db_dependency):
    features = FighterFeatures(
        fighter_id=fighter_id,
        avg_sig_str_landed=2.53,
        avg_sig_str_pct=0.69,
        avg_sub_att=0.00,
        avg_td_landed=4.04,
        avg_td_pct=0.59,
        wins_by_ko=1,
        wins_by_submission=6,
    )
    db.add(features)
    db.commit()
    return {"status": "good"}
