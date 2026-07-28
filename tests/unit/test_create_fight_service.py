import pytest

from app.infraestructure.database.models.fight_model import FightDB
from app.interfaces.schemas.fights import FightForm
from app.services.fights import create_fight_service

from .conftest import FIGHT_DATA, MagicMock, MockFighterRepo, MockFightRepo


class TestCreateFightService:
    def test_returns_created_fight(self, fight_form: FightForm, mock_fight_repo: MockFightRepo, mock_fighter_repo: MockFighterRepo, fight_db: FightDB):
        mock_fighter_repo.get_by_id.return_value = MagicMock()
        mock_fight_repo.create.return_value = fight_db
        result = create_fight_service(fight_form, mock_fight_repo, mock_fighter_repo)
        assert result == fight_db

    def test_calls_repo_create(self, fight_form: FightForm, mock_fight_repo: MockFightRepo, mock_fighter_repo: MockFighterRepo):
        mock_fighter_repo.get_by_id.return_value = MagicMock()
        mock_fight_repo.create.return_value = FightDB(**FIGHT_DATA)
        create_fight_service(fight_form, mock_fight_repo, mock_fighter_repo)
        mock_fight_repo.create.assert_called_once()

    def test_passes_fight_db_instance(self, fight_form: FightForm, mock_fight_repo: MockFightRepo, mock_fighter_repo: MockFighterRepo):
        mock_fighter_repo.get_by_id.return_value = MagicMock()
        mock_fight_repo.create.return_value = FightDB(**FIGHT_DATA)
        create_fight_service(fight_form, mock_fight_repo, mock_fighter_repo)
        call_arg = mock_fight_repo.create.call_args[0][0]
        assert isinstance(call_arg, FightDB)

    def test_fails_if_red_corner_not_found(self, fight_form: FightForm, mock_fight_repo: MockFightRepo, mock_fighter_repo: MockFighterRepo):
        mock_fighter_repo.get_by_id.side_effect = [None, MagicMock()]
        with pytest.raises(ValueError, match="red corner not found"):
            create_fight_service(fight_form, mock_fight_repo, mock_fighter_repo)

    def test_fails_if_blue_corner_not_found(self, fight_form: FightForm, mock_fight_repo: MockFightRepo, mock_fighter_repo: MockFighterRepo):
        mock_fighter_repo.get_by_id.side_effect = [MagicMock(), None]
        with pytest.raises(ValueError, match="blue corner not found"):
            create_fight_service(fight_form, mock_fight_repo, mock_fighter_repo)
