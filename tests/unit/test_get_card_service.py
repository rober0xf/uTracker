import pytest

from app.infraestructure.database.models.card_model import CardDB
from app.services.cards import get_all_cards_service, get_card_by_id_service

from .conftest import MagicMock, MockCardRepo


class TestGetAllCardsService:
    def test_returns_cards(self, mock_repo: MockCardRepo):
        mock_repo.get_all.return_value = [CardDB(), CardDB()]
        result = get_all_cards_service(mock_repo)
        assert result == mock_repo.get_all.return_value

    def test_calls_repo(self, mock_repo: MockCardRepo):
        mock_repo.get_all.return_value = [CardDB(), CardDB()]
        get_all_cards_service(mock_repo)
        mock_repo.get_all.assert_called_once()

    def test_fails_if_no_cards(self, mock_repo: MockCardRepo):
        mock_repo.get_all.return_value = []
        with pytest.raises(ValueError, match="no cards found"):
            get_all_cards_service(mock_repo)

    def test_fails_if_none(self, mock_repo: MockCardRepo):
        mock_repo.get_all.return_value = None
        with pytest.raises(ValueError, match="no cards found"):
            get_all_cards_service(mock_repo)


class TestGetCardByIDService:
    def test_returns_card(self, mock_repo: MockCardRepo, card_data: MagicMock):
        mock_repo.get_by_id.return_value = CardDB(**card_data.model_dump())
        result = get_card_by_id_service(1, mock_repo)
        assert result == mock_repo.get_by_id.return_value

    def test_calls_repo_with_id(self, mock_repo: MockCardRepo, card_data: MagicMock):
        mock_repo.get_by_id.return_value = CardDB(**card_data.model_dump())
        get_card_by_id_service(1, mock_repo)
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_fails_if_not_found(self, mock_repo: MockCardRepo):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match="card with id 99 not found"):
            get_card_by_id_service(99, mock_repo)

    @pytest.mark.parametrize("card_id", [1, 42, 999])
    def test_raises_with_correct_id(self, mock_repo: MockCardRepo, card_id):
        mock_repo.get_by_id.return_value = None
        with pytest.raises(ValueError, match=f"card with id {card_id} not found"):
            get_card_by_id_service(card_id, mock_repo)
