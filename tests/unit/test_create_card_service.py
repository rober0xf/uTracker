from datetime import date

import pytest

from app.infraestructure.database.models.card_model import CardDB
from app.interfaces.schemas.card import CardCreate
from app.services.cards import create_card_form_service, create_card_service

from .conftest import MagicMock, MockCardRepo


class TestCreateCardFormService:
    def test_create_form_correct_return(self):
        result = create_card_form_service(card_name="Emmett vs Vallejos", card_date=date(2026, 3, 14), card_number=327)
        assert isinstance(result, CardCreate)

    def test_create_form_successfull(self):
        result = create_card_form_service(card_name="Emmett vs Vallejos", card_date=date(2026, 3, 14), card_number=327)
        assert result.card_name == "Emmett vs Vallejos"
        assert result.card_date == date(2026, 3, 14)
        assert result.card_number == 327

    def test_create_form_optional_number(self):
        result = create_card_form_service(card_name="Emmett vs Vallejos", card_date=date(2026, 3, 14), card_number=None)
        assert result.card_name == "Emmett vs Vallejos"
        assert result.card_date == date(2026, 3, 14)
        assert result.card_number is None

    @pytest.mark.parametrize("card_number", [None, 1, 9999])
    def test_create_form_number_variants(self, card_number):
        result = create_card_form_service(card_name="Emmett vs Vallejos", card_date=date(2026, 3, 14), card_number=card_number)
        assert result.card_number == card_number


class TestCreateCardService:
    def test_calls_repo(self, card_data: MagicMock, mock_repo: MockCardRepo):
        create_card_service(card_data, mock_repo)
        mock_repo.create.assert_called_once()

    def test_passes_cards_db_instance(self, card_data: MagicMock, mock_repo: MockCardRepo):
        create_card_service(card_data, mock_repo)
        call_arg = mock_repo.create.call_args[0][0]
        assert isinstance(call_arg, CardDB)

    def test_maps_fields_to_cards_db(self, card_data: MagicMock, mock_repo: MockCardRepo):
        create_card_service(card_data, mock_repo)
        call_arg = mock_repo.create.call_args[0][0]
        assert call_arg.card_name == card_data.card_name
        assert call_arg.card_date == card_data.card_date
        assert call_arg.card_number == card_data.card_number

    def test_returns_repo_result(self, card_data: MagicMock, mock_repo: MockCardRepo):
        mock_repo.create.return_value = CardDB(**card_data.model_dump())
        result = create_card_service(card_data, mock_repo)
        assert result == mock_repo.create.return_value
