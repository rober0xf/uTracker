import json
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
import torch
import torch.nn as nn
from app.db.models import FighterFeatures


model = None

with open("pytorch/predictor_meta.json", "r") as f:
    metadata = json.load(f)


def get_pytorch_model():
    global model
    if model is None:
        checkpoint = torch.load("pytorch/predictor.pt", map_location="cpu")
        model = FightPredictor(input_dim=metadata["input_dim"])
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        print("pytorch model loaded")

    return model


class FightPredictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 1))

    def forward(self, x):
        return self.net(x)


class FighterFeaturesRequest(BaseModel):
    fighter_id: int


class FightPredictionRequest(BaseModel):
    red_corner_id: int
    blue_corner_id: int


class FightPredictionResponse(BaseModel):
    red_corner_id: int
    blue_corner_id: int
    red_corner_win_probability: float
    blue_corner_win_probability: float


async def get_or_fetch_fighter_features(fighter_id: int, db: Session) -> dict:
    stmt = select(FighterFeatures).where(FighterFeatures.fighter_id == fighter_id)
    features = db.execute(stmt).scalars().first()

    # if features and all(
    #     [
    #         features.avg_sig_str_landed,
    #         features.avg_sig_str_pct,
    #         features.avg_sub_att,
    #         features.avg_td_landed,
    #         features.avg_td_pct,
    #     ]
    # ):
    #     return features_to_dict(features)
    if features:
        return features_to_dict(features)

    raise HTTPException(status_code=400, detail=f"fighter {fighter_id} has no features")
    # fighter = db.execute(select(FightersDB).where(FightersDB.id == fighter_id)).scalars().first()
    #
    # if not fighter:
    #     raise HTTPException(status_code=404, detail=f"Fighter {fighter_id} not found")
    #
    # external_data = await get_external_fighter_features(fighter.name)
    # print(f"External API response: {external_data}")
    #
    # if not external_data:
    #     raise HTTPException(status_code=502, detail=f"Could not fetch data for fighter {fighter.name} from external API")
    #
    # update_fighter_features(db, fighter_id, external_data)
    # db.commit()
    #
    # # fetch updated features
    # updated_features = db.execute(stmt).scalars().first()
    # return features_to_dict(updated_features)


def features_to_dict(features: FighterFeatures | None) -> dict:
    if not features:
        raise ValueError("fighter features not found")
    return {
        "fighter_id": features.fighter_id,
        "avg_sig_str_landed": features.avg_sig_str_landed,
        "avg_sig_str_pct": features.avg_sig_str_pct,
        "avg_sub_att": features.avg_sub_att,
        "avg_td_landed": features.avg_td_landed,
        "avg_td_pct": features.avg_td_pct,
        "wins_by_ko": features.wins_by_ko,
        "wins_by_submission": features.wins_by_submission,
    }


def prepare_model_input(red_corner_features: dict, blue_corner_features: dict) -> torch.Tensor:
    feature_order = [
        "avg_sig_str_landed",
        "avg_sig_str_pct",
        "avg_sub_att",
        "avg_td_landed",
        "avg_td_pct",
        "wins_by_ko",
        "wins_by_submission",
    ]

    red_corner_vector = [red_corner_features[f] for f in feature_order]
    blue_corner_vector = [blue_corner_features[f] for f in feature_order]

    combined = red_corner_vector + blue_corner_vector
    return torch.tensor([combined], dtype=torch.float32)
