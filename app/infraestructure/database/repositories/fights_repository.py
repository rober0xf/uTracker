from models.fight_model import FightDB
from sqlalchemy.orm import Session


class FightRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[FightDB]:
        return self.db.query(FightDB).all()

    def get_by_id(self, fight_id: int) -> FightDB | None:
        return self.db.query(FightDB).filter(FightDB.id == fight_id).first()

    def create(self, fight: FightDB) -> FightDB:
        self.db.add(fight)
        self.db.commit()
        self.db.refresh(fight)
        return fight

    def update(self, fight: FightDB) -> FightDB:
        self.db.commit()
        self.db.refresh(fight)
        return fight

    def delete(self, fight_id: int) -> bool:
        result = self.db.query(FightDB).filter(FightDB.id == fight_id).delete(synchronize_session=False)
        self.db.commit()
        return bool(result)

    def save(self, fight: FightDB) -> FightDB:
        self.db.commit()
        self.db.refresh(fight)
        return fight
