from unittest.mock import MagicMock

import pytest

from app.infraestructure.database.models.fighter_model import FighterDB
from app.services.fighters import create_fighter_service

from .conftest import FIGHTER_DATA, MockFighterRepo


class TestCreateFighterService:
    def test_calls_to_fighter_base_data(self, fighter_form: MagicMock, mock_repo: MockFighterRepo):
        mock_repo.create.return_value = FighterDB(**FIGHTER_DATA)
        create_fighter_service(fighter_form, mock_repo)
        fighter_form.to_fighter_base_data.assert_called_once()

    def test_calls_repo_create(self, fighter_form: MagicMock, mock_repo: MockFighterRepo):
        mock_repo.create.return_value = FighterDB(**FIGHTER_DATA)
        create_fighter_service(fighter_form, mock_repo)
        mock_repo.create.assert_called_once()

    def test_passes_fighter_db_instance(self, fighter_form: MagicMock, mock_repo: MockFighterRepo):
        mock_repo.create.return_value = FighterDB(**FIGHTER_DATA)
        create_fighter_service(fighter_form, mock_repo)
        call_arg = mock_repo.create.call.args[0][0]
        assert isinstance(call_arg, FighterDB)

    def test_returns_repo_result(self, fighter_form: MagicMock, mock_repo: MockFighterRepo):
        expected = FighterDB(**FIGHTER_DATA)
        mock_repo.create.return_value = expected
        result = create_fighter_service(fighter_form, mock_repo)
        assert result == expected

    def test_fails_if_form_data_none(self, mock_repo: MockFighterRepo):
        form = MagicMock()
        form.to_fighter_base_data.return_value = None
        with pytest.raises(ValueError, match="error parsing the fighter data"):
            create_fighter_service(form, mock_repo)
