import pytest

from app.domain.enums.enums import DivisionEnum
from app.infraestructure.database.models.fighter_model import FighterDB
from app.interfaces.schemas.fighters import FighterUpdate
from app.services.fighters import get_all_fighters_service, get_fighter_by_id_service, get_fighter_update_form

from .conftest import MockFighterRepo


class TestGetAllFighterService:
    def test_returns_fighters(self, mock_repo: MockFighterRepo, fighter_db: FighterDB):
        mock_repo.get_all.return_value = [fighter_db]
        result = get_all_fighters_service(mock_repo)
        assert result == [fighter_db]

    def test_calls_repo(self, mock_repo: MockFighterRepo, fighter_db: FighterDB):
        mock_repo.get_all.return_value = [fighter_db]
        get_all_fighters_service(mock_repo)
        mock_repo.get_all.assert_called_once()

    def test_fails_if_empty(self, mock_repo: MockFighterRepo):
        mock_repo.get_all.return_value = []
        with pytest.raises(ValueError, match="no fighters found"):
            get_all_fighters_service(mock_repo)

    def test_fails_if_none(self, mock_repo: MockFighterRepo):
        mock_repo.get_all.return_value = None
        with pytest.raises(ValueError, match="no fighters found"):
            get_all_fighters_service(mock_repo)


class TestGetFighterByIDService:
    def test_returns_fighter(self, mock_repo: MockFighterRepo, fighter_db: FighterDB):
        mock_repo.get_by_id.return_value = fighter_db
        result = get_fighter_by_id_service(1, mock_repo)
        assert result == fighter_db

    def test_calls_repo_with_id(self, mock_repo: MockFighterRepo, fighter_db: FighterDB):
        mock_repo.get_by_id.return_value = fighter_db
        get_fighter_by_id_service(1, mock_repo)
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_fails_if_not_found(self, mock_repo: MockFighterRepo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="fighter not found"):
            get_fighter_by_id_service(999, mock_repo)


class TestGetFighterUpdateForm:
    @pytest.fixture
    def ef(self) -> dict:
        return {
            "name": "",
            "division": "",
            "wins": "",
            "losses": "",
            "draws": "",
            "no_contest": "",
            "height": "",
            "weight": "",
            "reach": "",
        }

    def test_returns_fighter_update(self, ef):
        result = get_fighter_update_form(**{**ef, "name": "Jon Jones"})
        assert isinstance(result, FighterUpdate)

    def test_maps_name(self, ef):
        result = get_fighter_update_form(**{**ef, "name": "Jon Jones"})
        assert result.name == "Jon Jones"

    def test_parses_division_enum(self, ef):
        result = get_fighter_update_form(**{**ef, "division": "heavyweight"})
        assert result.division == DivisionEnum.HEAVYWEIGHT

    def test_parses_int_fields(self, ef):
        result = get_fighter_update_form(**{**ef, "wins": "27", "losses": "1", "draws": "0"})
        assert result.wins == 27
        assert result.losses == 1
        assert result.draws == 0

    def test_none_fields_when_empty(self, ef):
        result = get_fighter_update_form(**ef)
        assert result.name is None
        assert result.division is None
        assert result.wins is None

    def test_parses_float_fields(self, ef):
        result = get_fighter_update_form(**{**ef, "height": "1.93", "weight": "77.0", "reach": "1.85"})
        assert result.height == 1.93
        assert result.weight == 77.0
        assert result.reach == 1.85
