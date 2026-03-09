from sqlalchemy.orm import Session

from app.infraestructure.database.models.card_model import CardDB


class CardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[CardDB]:
        return self.db.query(CardDB).all()

    def get_by_id(self, card_id: int) -> CardDB | None:
        return self.db.query(CardDB).filter(CardDB.id == card_id).first()

    def create(self, card: CardDB) -> CardDB:
        self.db.add(card)
        self.db.commit()
        self.db.refresh(card)
        return card

    def delete(self, card_id: int) -> bool:
        result = self.db.query(CardDB).filter(CardDB.id == card_id).delete(synchronize_session=False)
        self.db.commit()
        return bool(result)
