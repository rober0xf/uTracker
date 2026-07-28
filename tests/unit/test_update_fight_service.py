import pytest

from app.domain.enums.enums import WinningMethodEnum
from app.infraestructure.database.models.fight_model import FightDB
from app.interfaces.schemas.fights import FightUpdate
from app.services.fights import update_fight_service

from .conftest import MockFightRepo


class TestUpdateFightService:
    def test_fails_if_fight_not_found(self, mock_repo: MockFightRepo, fight_update: FightUpdate):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="fight not found"):
            update_fight_service(99, fight_update, mock_repo)

    def test_returns_current_fight_if_no_update_data(self, mock_repo: MockFightRepo, fight_db: FightDB, empty_update: FightUpdate):
        mock_repo.get_by_id.return_value = fight_db
        result = update_fight_service(1, empty_update, mock_repo)
        assert result == fight_db
        mock_repo.save.assert_not_called()

    def test_calls_save_on_changes(self, mock_repo: MockFightRepo, fight_db: FightDB, fight_update: FightUpdate):
        mock_repo.get_by_id.return_value = fight_db
        update_fight_service(1, fight_update, mock_repo)
        mock_repo.save.assert_called_once_with(fight_db)

    def test_does_not_save_if_same_values(self, mock_repo: MockFightRepo, fight_db: FightDB):
        same_update = FightUpdate(method=WinningMethodEnum.KO)
        mock_repo.get_by_id.return_value = fight_db
        update_fight_service(1, same_update, mock_repo)
        mock_repo.save.assert_not_called()

    def test_returns_fight(self, mock_repo: MockFightRepo, fight_db: FightDB, fight_update: FightUpdate):
        mock_repo.get_by_id.return_value = fight_db
        result = update_fight_service(1, fight_update, mock_repo)
        assert result == fight_db
