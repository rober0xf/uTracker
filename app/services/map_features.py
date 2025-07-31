from sqlalchemy.orm import Session

from app.db.features import FighterFeatures
from app.db.models import FightersDB

from .api_services import get_external_fighter_features


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


def create_fighter_with_features(session: Session, fighter_data):
    if hasattr(fighter_data, "model_dump"):
        fighter_dict = fighter_data.model_dump()
    elif hasattr(fighter_data, "dict"):
        fighter_dict = fighter_data.dict()
    elif isinstance(fighter_data, dict):
        fighter_dict = fighter_data
    else:
        raise ValueError("fighter_data debe ser un dict o un modelo Pydantic")

    fighter = FightersDB(**fighter_dict)
    session.add(fighter)
    session.flush()

    api_data = get_external_fighter_features(fighter.name)
    if api_data:
        update_fighter_features(session, fighter.id, api_data)
    session.commit()
    return fighter


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
