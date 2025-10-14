from sqlalchemy.orm import Session
from fastapi import Form

from app.db.models import FighterFeatures
from app.schemas.fighters import DivisionEnum, FightersUpdate


def to_float(value):
    if isinstance(value, str):
        return float(value.strip("%").split()[0])
    return float(value) if value else 0.0


def time_to_minutes(time):
    if not time:
        return 0
    mins, secs = time.split(":")
    return int(mins) + int(secs) / 60.0


def map_api_to_features(api_data):
    records = api_data.get("Records", {})
    win_stats = api_data.get("Win Stats", {})

    return {
        "avg_sig_str_landed": to_float(records.get("Sig. Str. Landed")),
        "avg_sig_str_pct": to_float(records.get("Striking accuracy")),
        "avg_sub_att": to_float(records.get("Submission avg")),
        "avg_td_landed": to_float(records.get("Takedown avg")),
        "avg_td_pct": to_float(records.get("Takedown Accuracy")),
        "wins_by_ko": int(win_stats.get("Wins by Knockout", 0)),
        "wins_by_submission": int(win_stats.get("Wins by Submission", 0)),
    }


def update_fighter_features(session: Session, fighter_id: int, api_data: dict):
    features_data = map_api_to_features(api_data)
    features = session.query(FighterFeatures).filter_by(fighter_id=fighter_id).first()
    if features:
        for key, val in features_data.items():
            setattr(features, key, val)
    else:
        features = FighterFeatures(fighter_id=fighter_id, **features_data)
        session.add(features)
    session.commit()


# we need to use this service because the way fastapi handles forms
async def get_fighter_update_form(
    name: str = Form(None),
    division: str = Form(None),
    wins: str = Form(None),
    losses: str = Form(None),
    draws: str = Form(None),
    no_contest: str = Form(None),
    height: str = Form(None),
    weight: str = Form(None),
    reach: str = Form(None),
) -> FightersUpdate:
    parsed_division = None
    if division:
        parsed_division = DivisionEnum(division)

    return FightersUpdate(
        name=name if name else None,
        division=parsed_division,
        birth_date=None,
        wins=int(wins) if wins and wins.strip() else None,
        losses=int(losses) if losses and losses.strip() else None,
        draws=int(draws) if draws and draws.strip() else None,
        no_contest=int(no_contest) if no_contest and no_contest.strip() else None,
        height=float(height) if height and height.strip() else None,
        weight=float(weight) if weight and weight.strip() else None,
        reach=float(reach) if reach and reach.strip() else None,
    )
