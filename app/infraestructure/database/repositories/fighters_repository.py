from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infraestructure.database.models.fighter_model import FighterDB, FighterFeatures
from app.services.map_features import map_api_to_features


class FighterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[FighterDB]:
        return self.db.query(FighterDB).all()

    def get_by_id(self, fighter_id: int) -> FighterDB | None:
        return self.db.query(FighterDB).filter(FighterDB.id == fighter_id).first()

    def create(self, fighter: FighterDB) -> FighterDB:
        self.db.add(fighter)
        self.db.commit()
        self.db.refresh(fighter)
        return fighter

    def update(self, fighter: FighterDB, data: dict) -> FighterDB:
        for field, value in data.items():
            setattr(fighter, field, value)
        fighter.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(fighter)
        return fighter

    def update_features(self, fighter_id: int, api_data: dict) -> FighterFeatures:
        features_data = map_api_to_features(api_data)
        features = self.db.query(FighterFeatures).filter_by(fighter_id=fighter_id).first()

        if features:
            for key, val in features_data.items():
                setattr(features, key, val)
        else:
            features = FighterFeatures(fighter_id=fighter_id, **features_data)
            self.db.add(features)
        self.db.commit()
        return features

    def delete(self, fighter_id: int) -> bool:
        result = self.db.query(FighterDB).filter(FighterDB.id == fighter_id).delete(synchronize_session=False)
        self.db.commit()
        return bool(result)

    def get_features_by_fighter_id(self, fighter_id: int):
        stmt = select(FighterFeatures).where(FighterFeatures.fighter_id == fighter_id)
        return self.db.execute(stmt).scalars().first()
