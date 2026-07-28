import pytest

from app.infraestructure.database.models.fighter_model import FighterDB
from app.interfaces.schemas.fighters import FighterUpdate
from app.services.fighters import update_fighter_service

from .conftest import MockFighterRepo


class TestUpdateFighterService:
    def test_raises_if_fighter_not_found(self, mock_repo: MockFighterRepo, fighter_update: FighterUpdate):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="fighter not found"):
            update_fighter_service(99, fighter_update, mock_repo)

    def test_returns_current_fighter_if_no_update_data(self, mock_repo: MockFighterRepo, fighter_db: FighterDB, empty_update: FighterUpdate):
        mock_repo.get_by_id.return_value = fighter_db
        result = update_fighter_service(1, empty_update, mock_repo)
        assert result == fighter_db
        mock_repo.update.assert_not_called()

    def test_calls_repo_update(self, mock_repo: MockFighterRepo, fighter_db: FighterDB, fighter_update: FighterUpdate):
        mock_repo.get_by_id.return_value = fighter_db
        mock_repo.update.return_value = fighter_db
        update_fighter_service(1, fighter_update, mock_repo)
        mock_repo.update.assert_called_once()
