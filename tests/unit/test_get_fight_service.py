import pytest

from app.infraestructure.database.models.fight_model import FightDB
from app.interfaces.schemas.fights import FightForm
from app.services.fights import get_all_fights_service, get_fight_by_id_service, get_fight_form

from .conftest import MockFightRepo


class TestGetFightForm:
    def test_returns_fight_form(self):
        result = get_fight_form(
            rounds="5",
            division="lightweight",
            method=None,
            card="1",
            red_corner=1,
            blue_corner=2,
            favorite="red_corner",
            fight_date="2026-03-14",
        )
        assert isinstance(result, FightForm)

    def test_maps_fields(self):
        result = get_fight_form(
            rounds="5",
            division="lightweight",
            method=None,
            card="1",
            red_corner=1,
            blue_corner=2,
            favorite="red_corner",
            fight_date="2026-03-14",
        )
        assert result.red_corner == 1
        assert result.blue_corner == 2
        assert result.favorite == "red_corner"

    def test_optional_fields_none(self):
        result = get_fight_form(
            rounds="5",
            division="lightweight",
            method=None,
            card="1",
            red_corner=1,
            blue_corner=2,
            round_finish=None,
            favorite="red_corner",
            fight_date="2026-03-14",
        )
        assert result.method is None
        assert result.winner is None


class TestGetAllFightsService:
    def test_returns_fights(self, mock_repo: MockFightRepo, fight_db: FightDB):
        mock_repo.get_all.return_value = [fight_db]
        result = get_all_fights_service(mock_repo)
        assert result == [fight_db]

    def test_calls_repo(self, mock_repo: MockFightRepo, fight_db: FightDB):
        mock_repo.get_all.return_value = [fight_db]
        get_all_fights_service(mock_repo)
        mock_repo.get_all.assert_called_once()

    def test_fails_if_empty(self, mock_repo: MockFightRepo):
        mock_repo.get_all.return_value = []
        with pytest.raises(ValueError, match="no fights found"):
            get_all_fights_service(mock_repo)

    def test_fails_if_None(self, mock_repo: MockFightRepo):
        mock_repo.get_all.return_value = None
        with pytest.raises(ValueError, match="no fights found"):
            get_all_fights_service(mock_repo)


class TestGetFightByIDService:
    def test_returns_fight(self, mock_repo: MockFightRepo, fight_db: FightDB):
        mock_repo.get_by_id.return_value = fight_db
        result = get_fight_by_id_service(1, mock_repo)
        assert result == fight_db

    def test_calls_repo_with_id(self, mock_repo: MockFightRepo, fight_db: FightDB):
        mock_repo.get_by_id.return_value = fight_db
        get_fight_by_id_service(1, mock_repo)
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_fails_if_not_found(self, mock_repo: MockFightRepo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="fight with id 99 not found"):
            get_fight_by_id_service(99, mock_repo)

    @pytest.mark.parametrize("fight_id", [1, 42, 999])
    def test_fails_with_correct_id_in_message(self, mock_repo: MockFightRepo, fight_id):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match=f"fight with id {fight_id} not found"):
            get_fight_by_id_service(fight_id, mock_repo)
